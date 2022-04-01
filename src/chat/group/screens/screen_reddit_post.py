import logging
import os

from praw.models import Submission
from telegram.error import BadRequest
from telegram.ext import CallbackContext
from telegram.message import Message

import constants as c
import resources.Environment as Env
from src.model.RedditGroupPost import RedditGroupPost
from src.model.SavedMedia import SavedMedia
from src.model.enums.SavedMediaType import SavedMediaType
from src.model.pojo.Reddit import Reddit
from src.service.download_service import download_temp_file
from src.service.image_service import compress_image
from src.service.message_service import full_media_send, escape_valid_markdown_chars


def manage(context: CallbackContext) -> None:
    """
    Send a reddit post to the chat group
    :param context: Context of callback
    """

    job = context.job

    reddit = Reddit(client_id=Env.REDDIT_CLIENT_ID.get(),
                    client_secret=Env.REDDIT_CLIENT_SECRET.get(),
                    user_agent=Env.REDDIT_USER_AGENT.get())

    subreddit_name = str(job.context)

    # Get first 10 hot posts
    for post in reddit.get_subreddit_hot_posts(subreddit_name, 10):
        post: Submission = post

        # Post is valid if it's not stickied and not nsfw
        if not post.stickied and not post.over_18:
            try:
                # Check if it has already been posted
                RedditGroupPost.get(RedditGroupPost.short_link == post.shortlink)
            except RedditGroupPost.DoesNotExist:
                # Caption
                author_name = post.author.name
                author_url = c.REDDIT_USER_URL_PREFIX + post.author.name
                subreddit_url = c.REDDIT_SUBREDDIT_URL_PREFIX + post.subreddit.display_name

                caption = '[{}]({})'.format(escape_valid_markdown_chars(post.title), post.shortlink)
                caption += '\n\n'
                caption += '_Posted by [u/{}]({}) on [r/{}]({})_' \
                    .format(escape_valid_markdown_chars(author_name), author_url,
                            escape_valid_markdown_chars(post.subreddit.display_name), subreddit_url)

                # Send in group
                try:
                    # Send only media
                    if post.url.startswith('https://i.redd.it') or post.url.startswith('https://v.redd.it'):
                        saved_media: SavedMedia = SavedMedia()
                        if post.url.startswith('https://v.redd.it'):
                            saved_media.type = SavedMediaType.VIDEO.value
                        elif post.url.endswith('.gif'):
                            saved_media.type = SavedMediaType.ANIMATION.value
                        else:
                            saved_media.type = SavedMediaType.PHOTO.value
                        saved_media.media_id = post.url

                        try:
                            # If video, download to local
                            if saved_media.type == SavedMediaType.VIDEO.value:
                                try:
                                    url = post.media['reddit_video']['fallback_url']
                                    url = url.split("?")[0]
                                    saved_media.media_id = open(download_temp_file(url), 'rb')
                                except KeyError:
                                    logging.error('Reddit post {} has no video'.format(post.shortlink))
                                    continue

                            # Send media
                            message: Message = full_media_send(context, saved_media, caption=caption,
                                                               chat_id=Env.OPD_GROUP_ID.get_int())
                        except BadRequest as exceptionBadRequest:
                            # Resize if type is image
                            if saved_media.type == SavedMediaType.PHOTO.value:
                                logging.error('Error sending image {}. Trying to resize it.'.format(post.url))

                                # Try resending with a smaller image
                                image_path = compress_image(post.url, c.TG_DEFAULT_IMAGE_COMPRESSION_QUALITY)
                                saved_media.media_id = open(image_path, 'rb')
                                message: Message = full_media_send(context, saved_media, caption=caption,
                                                                   chat_id=Env.OPD_GROUP_ID.get_int())

                                try:
                                    # Delete the temporary image
                                    os.remove(image_path)
                                except OSError:
                                    # Ignore, will be deleted by auto-cleanup timer
                                    logging.warning('Error deleting temporary image {}'.format(image_path))
                                    pass
                            else:
                                raise exceptionBadRequest

                        # Save post
                        reddit_group_post: RedditGroupPost = RedditGroupPost()
                        reddit_group_post.short_link = post.shortlink
                        reddit_group_post.message_id = message.message_id
                        reddit_group_post.save()
                        break
                except BadRequest as bad_request:  # Try again if BadRequest
                    logging.error('Error sending reddit post {}: {}'.format(post.shortlink, bad_request))
                    continue
                except Exception as e:  # Stop if any other error
                    logging.error('Error sending reddit post {}: {}'.format(post.shortlink, e))
                    raise e

import logging
import os

from praw.models import Submission
from telegram.error import BadRequest
from telegram.ext import CallbackContext
from telegram.message import Message

import constants as c
from src.model.RedditGroupPost import RedditGroupPost
from src.model.SavedMedia import SavedMedia
from src.model.enums.SavedMediaType import SavedMediaType
from src.model.pojo.Reddit import Reddit
from src.service.image_service import compress_image
from src.service.message_service import full_message_send, full_media_send, escape_valid_markdown_chars


def manage(context: CallbackContext) -> None:
    """
    Send a reddit post to the chat group
    :param context: Context of callback
    """

    job = context.job

    reddit = Reddit(client_id=os.environ[c.ENV_REDDIT_CLIENT_ID],
                    client_secret=os.environ[c.ENV_REDDIT_CLIENT_SECRET],
                    user_agent=os.environ[c.ENV_REDDIT_USER_AGENT])

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
                    if post.url.startswith('https://i.redd.it'):
                        saved_media: SavedMedia = SavedMedia()
                        saved_media.type = SavedMediaType.PHOTO.value
                        saved_media.media_id = post.url
                        try:
                            # Send image
                            message: Message = full_media_send(context, saved_media, caption=caption,
                                                               chat_id=os.environ[c.ENV_OPD_GROUP_ID])
                        except BadRequest:
                            logging.error('Error sending image {}. Trying to resize it.'.format(post.url))

                            # Try resending with a smaller image
                            image_path = compress_image(post.url, c.TG_DEFAULT_IMAGE_COMPRESSION_QUALITY)
                            saved_media.media_id = open(image_path, 'rb')
                            message: Message = full_media_send(context, saved_media, caption=caption,
                                                               chat_id=os.environ[c.ENV_OPD_GROUP_ID])

                            try:
                                # Delete the temporary image
                                os.remove(image_path)
                            except OSError:
                                # Ignore, will be deleted by auto-cleanup timer
                                logging.warning('Error deleting temporary image {}'.format(image_path))
                                pass

                    else:
                        # Send link
                        message: Message = full_message_send(context, caption, chat_id=os.environ[c.ENV_OPD_GROUP_ID])

                    # Save post
                    reddit_group_post: RedditGroupPost = RedditGroupPost()
                    reddit_group_post.short_link = post.shortlink
                    reddit_group_post.message_id = message.message_id
                    reddit_group_post.save()

                    break
                except BadRequest as bad_request:  # Try again if BadRequest
                    logging.error('Error sending reddit post {}: {}'.format(post.shortlink, bad_request))
                    pass
                except Exception as e:  # Stop if any other error
                    logging.error('Error sending reddit post {}: {}'.format(post.shortlink, e))
                    raise e

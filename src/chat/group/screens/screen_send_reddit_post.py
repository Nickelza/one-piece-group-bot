import logging
import os

import telegram.error
from telegram.ext import CallbackContext
from telegram.utils.helpers import escape_markdown

import constants as const
from src.model.RedditGroupPost import RedditGroupPost
from src.model.pojo.Reddit import Reddit
from src.service.image_service import compress_image
import src.chat.group.group_chat_manager as group_chat_manager


def manage(context: CallbackContext) -> None:
    """
    Send a reddit post to the chat group
    :param context: context of callback
    :type context: CallbackContext
    """

    db = group_chat_manager.init()

    print('Running timer: ' + context.job.name)

    job = context.job

    reddit = Reddit(client_id=os.environ[const.ENV_REDDIT_CLIENT_ID],
                    client_secret=os.environ[const.ENV_REDDIT_CLIENT_SECRET],
                    user_agent=os.environ[const.ENV_REDDIT_USER_AGENT])

    subreddit_name = str(job.context)

    # Get first 10 hot posts
    for post in reddit.get_subreddit_hot_posts(subreddit_name, 10):
        # Post is valid if it's not stickied and not nsfw
        if not post.stickied and not post.over_18:
            try:
                # Check if it has already been posted
                RedditGroupPost.get(RedditGroupPost.short_link == post.shortlink)
            except RedditGroupPost.DoesNotExist:
                # Caption
                author_name = post.author.name
                author_url = const.REDDIT_USER_URL_PREFIX + post.author.name
                subreddit_url = const.REDDIT_SUBREDDIT_URL_PREFIX + post.subreddit.display_name

                caption = '[{}]({})'.format(escape_markdown(post.title, 2), escape_markdown(post.shortlink, 2))
                caption += '\n\n'
                caption += '_Posted by [u/{}]({}) on [r/{}]({})_' \
                    .format(escape_markdown(author_name, 2), escape_markdown(author_url, 2),
                            escape_markdown(post.subreddit.display_name, 2), escape_markdown(subreddit_url, 2))

                # Send in group
                try:
                    if post.url.startswith('https://i.redd.it'):
                        try:
                            # Send image
                            message = context.bot.send_photo(os.environ[const.ENV_OPD_GROUP_ID], photo=post.url,
                                                             caption=caption,
                                                             parse_mode=const.TG_DEFAULT_PARSE_MODE)
                        except telegram.error.BadRequest:
                            logging.error('Error sending image {}. Trying to resize it.'.format(post.url))

                            # Try resending with a smaller image
                            image_path = compress_image(post.url, const.TG_DEFAULT_IMAGE_COMPRESSION_QUALITY)
                            photo = open(image_path, 'rb')
                            message = context.bot.send_photo(os.environ[const.ENV_OPD_GROUP_ID], photo=photo,
                                                             caption=caption,
                                                             parse_mode=const.TG_DEFAULT_PARSE_MODE)

                            try:
                                # Delete the temporary image
                                os.remove(image_path)
                            except OSError:
                                # Ignore, will be deleted by auto-cleanup timer
                                logging.warning('Error deleting temporary image {}'.format(image_path))
                                pass

                    else:
                        # Send link
                        message = context.bot.send_message(os.environ[const.ENV_OPD_GROUP_ID], text=caption,
                                                           parse_mode=const.TG_DEFAULT_PARSE_MODE)

                    # Save post
                    RedditGroupPost.create(short_link=post.shortlink, message_id=message.message_id)

                    break
                except telegram.error.BadRequest as bad_request:  # Try again if BadRequest
                    logging.error('Error sending reddit post {}: {}'.format(post.shortlink, bad_request))
                    pass
                except Exception as e:  # Stop if any other error
                    logging.error('Error sending reddit post {}: {}'.format(post.shortlink, e))
                    break

    group_chat_manager.end(db)


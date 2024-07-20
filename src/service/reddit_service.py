import logging
import os
from typing import AsyncIterator

import asyncpraw
from asyncpraw import Reddit
from asyncpraw.models import Submission, Subreddit
from peewee import DoesNotExist
from telegram import Message
from telegram.error import BadRequest
from telegram.ext import ContextTypes

import constants as c
import resources.Environment as Env
from src.model.RedditGroupPost import RedditGroupPost
from src.model.enums.SavedMedia import SavedMedia
from src.model.enums.SavedMediaType import SavedMediaType
from src.service.message_service import full_media_send, escape_valid_markdown_chars
from src.utils.download_utils import download_temp_file
from src.utils.image_utils import compress_image


async def manage(context: ContextTypes.DEFAULT_TYPE, subreddit_name: str) -> None:
    """
    Send a reddit post to the chat group_chat
    :param context: Context of callback
    :param subreddit_name: Name of the subreddit
    """

    main_group_id = Env.MAIN_GROUP_ID.get()
    if main_group_id is None:
        logging.error("Main group ID is not set, can't send reddit post")
        return

    # Create connection
    connection: Reddit = asyncpraw.Reddit(
        client_id=Env.REDDIT_CLIENT_ID.get(),
        client_secret=Env.REDDIT_CLIENT_SECRET.get(),
        user_agent=Env.REDDIT_USER_AGENT.get(),
    )

    # Get first 10 hot posts
    subreddit: Subreddit = await connection.subreddit(subreddit_name)
    hot_posts: AsyncIterator = subreddit.hot(limit=10)

    async for post in hot_posts:
        post: Submission = post  # Type hinting

        # Post stickied - skip
        if post.stickied:
            continue

        # Post nsfw - skip
        if post.over_18:
            continue

        # Post already sent - skip
        try:
            RedditGroupPost.get(RedditGroupPost.short_link == post.shortlink)
            continue
        except DoesNotExist:
            pass

        # Caption
        author_name = post.author.name
        author_url = c.REDDIT_USER_URL_PREFIX + post.author.name
        subreddit_url = c.REDDIT_SUBREDDIT_URL_PREFIX + post.subreddit.display_name

        caption = "[{}]({})".format(escape_valid_markdown_chars(post.title), post.shortlink)
        caption += "\n\n"
        caption += "_Posted by [u/{}]({}) on [r/{}]({})_".format(
            escape_valid_markdown_chars(author_name),
            author_url,
            escape_valid_markdown_chars(post.subreddit.display_name),
            subreddit_url,
        )

        # Send in group_chat
        try:
            # Send only media
            if post.url.startswith("https://i.redd.it") or post.url.startswith(
                "https://v.redd.it"
            ):
                saved_media: SavedMedia = SavedMedia()
                if post.url.startswith("https://v.redd.it"):
                    saved_media.type = SavedMediaType.VIDEO
                elif post.url.endswith(".gif"):
                    saved_media.type = SavedMediaType.ANIMATION
                else:
                    saved_media.type = SavedMediaType.PHOTO
                saved_media.media_id = post.url

                try:
                    # If video, download to local
                    if saved_media.type == SavedMediaType.VIDEO:
                        try:
                            url = post.media["reddit_video"]["fallback_url"]
                            url = url.split("?")[0]
                            with open(download_temp_file(url), "rb") as media_id:
                                saved_media.media_id = media_id.read()
                        except KeyError:
                            logging.error("Reddit post {} has no video".format(post.shortlink))
                            continue

                    # Send media
                    message: Message = await full_media_send(
                        context, saved_media, caption=caption, chat_id=main_group_id
                    )
                except BadRequest as exceptionBadRequest:
                    # Resize if type is image
                    if saved_media.type == SavedMediaType.PHOTO:
                        logging.error(
                            "Error sending image {}. Trying to resize it.".format(post.url)
                        )

                        # Try resending with a smaller image
                        image_path = compress_image(
                            post.url, c.TG_DEFAULT_IMAGE_COMPRESSION_QUALITY
                        )
                        with open(image_path, "rb") as media_id:
                            saved_media.media_id = media_id.read()
                        message: Message = await full_media_send(
                            context,
                            saved_media,
                            caption=caption,
                            chat_id=main_group_id,
                        )

                        try:
                            # Delete the temporary image
                            os.remove(image_path)
                        except OSError:
                            # Ignore, will be deleted by auto-cleanup timer
                            logging.warning("Error deleting temporary image {}".format(image_path))
                            pass
                    else:
                        raise exceptionBadRequest

                # Save post
                reddit_group_post: RedditGroupPost = RedditGroupPost()
                reddit_group_post.short_link = post.shortlink
                reddit_group_post.message_id = message.message_id
                reddit_group_post.save()

                # If saved posts > 20, delete all but the last 20
                if RedditGroupPost.select().count() > 20:
                    last_n_posts = list(
                        RedditGroupPost.select().order_by(RedditGroupPost.id.desc()).limit(20)
                    )
                    (
                        RedditGroupPost.delete()
                        .where(RedditGroupPost.id.not_in([p.id for p in last_n_posts]))
                        .execute()
                    )

                break
        except BadRequest as bad_request:  # Try again if BadRequest
            logging.error("Error sending reddit post {}: {}".format(post.shortlink, bad_request))
            continue
        except Exception as e:  # Stop if any other error
            logging.error("Error sending reddit post {}: {}".format(post.shortlink, e))
            raise e

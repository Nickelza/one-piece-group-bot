from telegram import Update
from telegram.ext import ContextTypes

from resources import phrases
from src.model.enums.ContextDataKey import ContextDataKey
from src.model.error.CommonChatError import CommonChatException
from src.model.pojo.ContextDataValue import ContextDataValue
from src.service.bot_service import get_user_context_data
from src.service.message_service import full_inline_query_answer


async def manage(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """
    Main function for the group chat chat manager
    :param update: Telegram update
    :param context: Telegram context
    :return: None
    """

    query = update.inline_query.query

    if query == "":
        return

    try:
        context_data = get_user_context_data(context, ContextDataKey.INLINE_QUERY, inner_key=query)
    except CommonChatException:
        context_data = ContextDataValue(phrases.INLINE_QUERY_ITEM_NOT_FOUND_TITLE,
                                        phrases.INLINE_QUERY_ITEM_NOT_FOUND_MESSAGE,
                                        description=phrases.INLINE_QUERY_ITEM_NOT_FOUND_DESCRIPTION)

    await full_inline_query_answer(update, [context_data])

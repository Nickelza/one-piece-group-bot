from datetime import datetime

from telegram.ext import CallbackContext, ContextTypes

from src.model.enums.ContextDataKey import ContextDataKey, ContextDataType
from src.model.error.CommonChatError import CommonChatException


def get_context_data(
    context: ContextTypes.DEFAULT_TYPE,
    data_type: ContextDataType,
    key: ContextDataKey,
    inner_key: str = None,
    tolerate_key_exception: bool = True,
) -> any:
    """
    Get the bot context data
    :param context: The context
    :param data_type: The type
    :param key: The key
    :param inner_key: The inner key
    :param tolerate_key_exception: If the key is not found, raise CommonChatException instead of
    KeyError
    :return: The data
    """

    data = context.bot_data if data_type is ContextDataType.BOT else context.user_data

    try:
        if inner_key is not None:
            return data[key]["value"][inner_key]["value"]
        else:
            return data[key]["value"]
    except KeyError as e:
        if tolerate_key_exception:
            raise CommonChatException(
                f"Key {key} not found in context user data, this might be due to a system restart"
            )
        else:
            raise e


def set_context_data(
    context: ContextTypes.DEFAULT_TYPE,
    data_type: ContextDataType,
    key: ContextDataKey,
    value: any,
    inner_key: str = None,
) -> None:
    """
    Set the bot context data
    :param context: The context
    :param data_type: The type
    :param key: The key
    :param value: The value
    :param inner_key: The inner key
    :return: None
    """

    data = context.bot_data if data_type is ContextDataType.BOT else context.user_data

    if key not in data:
        data[key] = {"value": {}}

    if inner_key is not None:
        data[key]["value"][inner_key] = {"value": value}
        data[key]["value"][inner_key]["last_updated"] = datetime.now()
    else:
        data[key]["value"] = value
        data[key]["last_updated"] = datetime.now()


def remove_context_data(
    context: ContextTypes.DEFAULT_TYPE,
    data_type: ContextDataType,
    key: ContextDataKey,
    inner_key: str = None,
) -> None:
    """
    Remove the bot context data
    :param context: The context
    :param data_type: The type
    :param key: The key
    :param inner_key: The inner key
    :return: None
    """

    data = context.bot_data if data_type is ContextDataType.BOT else context.user_data

    if key not in data:
        return

    if inner_key is not None:
        data[key]["value"].pop(inner_key)
    else:
        data.pop(key)


def get_bot_context_data(
    context: CallbackContext,
    key: ContextDataKey,
    inner_key: str = None,
    tolerate_key_exception: bool = True,
) -> any:
    """
    Get the bot context data
    :param context: The context
    :param key: The key
    :param inner_key: The inner key
    :param tolerate_key_exception: If the key is not found, raise CommonChatException instead of
    KeyError
    :return: The data
    """

    return get_context_data(context, ContextDataType.BOT, key, inner_key, tolerate_key_exception)


def set_bot_context_data(
    context: CallbackContext, key: ContextDataKey, value: any, inner_key: str = None
) -> None:
    """
    Set the bot context data
    :param context: The context
    :param key: The key
    :param value: The value
    :param inner_key: The inner key
    :return: None
    """

    set_context_data(context, ContextDataType.BOT, key, value, inner_key)


def get_user_context_data(
    context: CallbackContext,
    key: ContextDataKey,
    inner_key: str = None,
    tolerate_key_exception: bool = True,
) -> any:
    """
    Get the user context data
    :param context: The context
    :param key: The key
    :param inner_key: The inner key
    :param tolerate_key_exception: If the key is not found, raise CommonChatException instead of
    KeyError
    :return: The data
    """

    return get_context_data(context, ContextDataType.USER, key, inner_key, tolerate_key_exception)


def set_user_context_data(
    context: CallbackContext, key: ContextDataKey, value: any, inner_key: str = None
) -> None:
    """
    Set the user context data
    :param context: The context
    :param key: The key
    :param value: The value
    :param inner_key: The inner key
    :return: None
    """

    set_context_data(context, ContextDataType.USER, key, value, inner_key)

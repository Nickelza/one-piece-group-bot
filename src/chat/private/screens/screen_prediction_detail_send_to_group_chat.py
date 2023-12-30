from enum import StrEnum

from telegram import Update, Message
from telegram.error import TelegramError
from telegram.ext import ContextTypes

import constants as c
from resources import phrases
from src.model.Group import Group
from src.model.GroupChat import GroupChat
from src.model.GroupUser import GroupUser
from src.model.Prediction import Prediction
from src.model.PredictionGroupChatMessage import PredictionGroupChatMessage
from src.model.User import User
from src.model.enums.PredictionStatus import PredictionStatus
from src.model.error.CustomException import PredictionException
from src.model.pojo.Keyboard import Keyboard
from src.service.message_service import full_message_send
from src.service.prediction_service import (
    prediction_is_sent_to_group_chat,
    get_prediction_text,
    get_prediction_deeplink_button,
)


class PredictionDetailsSendReservedKeys(StrEnum):
    """
    The reserved keys for this screen
    """

    PREDICTION_ID = "a"
    GROUP_CHAT_ID = "b"


async def manage(
    update: Update, context: ContextTypes.DEFAULT_TYPE, inbound_keyboard: Keyboard, user: User
) -> None:
    """
    Manage the prediction detail send to group screen
    :param update: The update
    :param context: The context
    :param inbound_keyboard: The inbound keyboard
    :param user: The user
    :return: None
    """

    prediction: Prediction = Prediction.get(
        Prediction.id == inbound_keyboard.get_int(PredictionDetailsSendReservedKeys.PREDICTION_ID)
    )

    # Send prediction to group chat
    if PredictionDetailsSendReservedKeys.GROUP_CHAT_ID in inbound_keyboard.info:
        group_chat: GroupChat = GroupChat.get_by_id(
            inbound_keyboard.get_int(PredictionDetailsSendReservedKeys.GROUP_CHAT_ID)
        )

        try:
            # Check that prediction is not closed
            if prediction.get_status() is not PredictionStatus.SENT:
                raise PredictionException(phrases.PREDICTION_IN_WRONG_STATUS)

            # Check that user is still admin
            group: Group = group_chat.group
            if not await user.is_chat_admin(context=context, chat_id=group.tg_group_id):
                GroupUser.set_no_longer_admin(user, group_chat.group)
                raise PredictionException(phrases.PREDICTION_SEND_TO_GROUP_NOT_ADMIN)

            # Check that prediction has not already been sent to the group chat
            if prediction_is_sent_to_group_chat(prediction, group_chat):
                raise PredictionException(phrases.PREDICTION_SEND_TO_GROUP_ALREADY_SENT)

            text = get_prediction_text(prediction)
            inline_keyboard = (
                [[get_prediction_deeplink_button(prediction)]]
                if prediction.get_status() is PredictionStatus.SENT
                else None
            )
            try:
                message: Message = await full_message_send(
                    context, text, group_chat=group_chat, keyboard=inline_keyboard
                )

                prediction_group_chat_message: PredictionGroupChatMessage = (
                    PredictionGroupChatMessage()
                )
                prediction_group_chat_message.prediction = prediction
                prediction_group_chat_message.group_chat = group_chat
                prediction_group_chat_message.message_id = message.message_id
                prediction_group_chat_message.save()

            except TelegramError as e:
                # Alert with error
                await full_message_send(context, str(e), update=update, show_alert=True)
        except PredictionException as e:
            # Alert with error
            await full_message_send(context, str(e), update=update, show_alert=True)

    # Build text
    added_text = ""
    inline_keyboard: list[list[Keyboard]] = []

    # Get group chats of groups where the user is admin
    admin_group_chats = (
        GroupChat.select()
        .join(Group)
        .join(GroupUser)
        .where(
            (GroupChat.is_active == True) & (GroupUser.user == user) & (GroupUser.is_admin == True)
        )
    )

    # User in not admin of any groups
    if len(admin_group_chats) == 0:
        added_text = phrases.PREDICTION_SEND_TO_GROUP_NO_GROUPS
    else:
        sent_group_chats: list[GroupChat] = []
        available_group_chats: list[GroupChat] = []

        for group_chat in admin_group_chats:
            group: Group = group_chat.group
            if await user.is_chat_admin(context=context, chat_id=group.tg_group_id):
                if prediction_is_sent_to_group_chat(prediction, group_chat):
                    sent_group_chats.append(group_chat)
                else:
                    available_group_chats.append(group_chat)
            else:
                GroupUser.set_no_longer_admin(user, group_chat.group)

        # Sent group chats
        if len(sent_group_chats) > 0:
            items_text = ""
            for index, group_chat in enumerate(sent_group_chats):
                items_text += phrases.PREDICTION_SEND_TO_GROUP_GROUPS_ALREADY_SENT_ITEM.format(
                    group_chat.get_full_name()
                )

            added_text += phrases.PREDICTION_SEND_TO_GROUP_GROUPS_ALREADY_SENT.format(items_text)

        # Available group chats
        if len(available_group_chats) > 0:
            items_text = ""
            keyboard_line: list[Keyboard] = []
            for index, group_chat in enumerate(available_group_chats):
                current_number = index + 1
                items_text += phrases.PREDICTION_SEND_TO_GROUP_GROUPS_AVAILABLE_ITEM.format(
                    index + 1, group_chat.get_full_name()
                )

                # Add button
                button_info = {PredictionDetailsSendReservedKeys.GROUP_CHAT_ID: group_chat.id}
                button = Keyboard(
                    str(current_number),
                    screen=inbound_keyboard.screen,
                    info=button_info,
                    inbound_info=inbound_keyboard.info,
                )
                keyboard_line.append(button)

                # Add new keyboard line if needed
                if (index + 1) % c.STANDARD_LIST_KEYBOARD_ROW_SIZE == 0 and index != 0:
                    inline_keyboard.append(keyboard_line)
                    keyboard_line = []

            # Add last keyboard line if needed
            if len(keyboard_line) > 0:
                inline_keyboard.append(keyboard_line)

            added_text += phrases.PREDICTION_SEND_TO_GROUP_GROUPS_AVAILABLE.format(items_text)

    ot_text = phrases.PREDICTION_SEND_TO_GROUP.format(added_text)

    await full_message_send(
        context,
        ot_text,
        update=update,
        keyboard=inline_keyboard,
        inbound_keyboard=inbound_keyboard,
    )

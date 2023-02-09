import json

from telegram import Update
from telegram.ext import ContextTypes

from src.chat.tgrest.screens.screen_prediction import manage as manage_screen_prediction
from src.chat.tgrest.screens.screen_send_private_message import manage as manage_screen_send_private_message
from src.model.enums.Notification import ImpelDownNotificationRestrictionPlaced, DevilFruitAwardedNotification
from src.model.enums.Notification import ImpelDownNotificationRestrictionRemoved
from src.model.enums.devil_fruit.DevilFruitSource import DevilFruitSource
from src.model.error.CustomException import DevilFruitValidationException
from src.model.tgrest.TgRest import TgRest, TgRestException
from src.model.tgrest.TgRestDevilFruitAward import TgRestDevilFruitAward
from src.model.tgrest.TgRestImpelDownNotification import TgRestImpelDownNotification
from src.model.tgrest.TgRestObjectType import TgRestObjectType
from src.model.tgrest.TgRestPrediction import TgRestPrediction
from src.model.tgrest.TgRestPrivateMessage import TgRestPrivateMessage
from src.service.devil_fruit_service import give_devil_fruit_to_user
from src.service.message_service import full_message_send, escape_valid_markdown_chars
from src.service.notification_service import send_notification


async def manage(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """
    Main function for the group chat chat manager
    :param update: Telegram update
    :param context: Telegram context
    :return: None
    """

    try:
        # Try parsing object
        try:
            # Try parsing object
            try:
                # If starts with "Error" or "Request", ignore
                if (update.effective_message.text.startswith("Error")
                        or update.effective_message.text.startswith("Request")):
                    return
            except AttributeError:
                return

            tg_rest_dict = json.loads(update.effective_message.text)
            tg_rest = TgRest(**tg_rest_dict)
        except Exception as tgre:
            raise TgRestException(str(tgre))

        # If not intended recipient, ignore
        if int(tg_rest.bot_id) != int(update.effective_message.get_bot().id):
            return

        match tg_rest.object_type:
            case TgRestObjectType.PREDICTION:
                tg_rest_prediction = TgRestPrediction(**tg_rest_dict)
                await manage_screen_prediction(context, tg_rest_prediction)

            case TgRestObjectType.PRIVATE_MESSAGE:
                tg_rest_private_message = TgRestPrivateMessage(**tg_rest_dict)
                await manage_screen_send_private_message(context, tg_rest_private_message)

            case TgRestObjectType.IMPEL_DOWN_NOTIFICATION:
                tg_rest_impel_down_notification = TgRestImpelDownNotification(**tg_rest_dict)
                if tg_rest_impel_down_notification.restriction_removed():
                    notification = ImpelDownNotificationRestrictionRemoved()
                else:
                    notification = ImpelDownNotificationRestrictionPlaced(
                        tg_rest_impel_down_notification.sentence_type,
                        tg_rest_impel_down_notification.release_date_time,
                        tg_rest_impel_down_notification.bounty_action,
                        tg_rest_impel_down_notification.reason)

                await send_notification(context, tg_rest_impel_down_notification.user, notification)

            case TgRestObjectType.DEVIL_FRUIT_AWARD:
                tg_rest_dfa = TgRestDevilFruitAward(**tg_rest_dict)

                # Give devil fruit to user
                try:
                    give_devil_fruit_to_user(tg_rest_dfa.devil_fruit, tg_rest_dfa.user, DevilFruitSource.ADMIN,
                                             reason=tg_rest_dfa.reason)
                except DevilFruitValidationException as e:
                    raise TgRestException(str(e))

                # Send notification
                notification = DevilFruitAwardedNotification(tg_rest_dfa.devil_fruit, tg_rest_dfa.reason)
                await send_notification(context, tg_rest_dfa.user, notification)

            case _:
                raise TgRestException("Unknown object type")
        await full_message_send(context, "Request received", update=update, quote=True)
    except TgRestException as e:
        await full_message_send(context, "Error: " + escape_valid_markdown_chars(e.message), update=update, quote=True)
        return

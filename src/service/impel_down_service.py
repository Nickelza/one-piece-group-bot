from datetime import datetime

from peewee import Update
from telegram.ext import ContextTypes

from resources import phrases
from src.model.ImpelDownLog import ImpelDownLog
from src.model.User import User
from src.model.enums.Notification import (
    ImpelDownNotificationRestrictionPlaced,
    ImpelDownBailPostedNotification,
)
from src.model.enums.ReservedKeyboardKeys import ReservedKeyboardKeys
from src.model.enums.Screen import Screen
from src.model.enums.impel_down.ImpelDownBountyAction import ImpelDownBountyAction
from src.model.enums.impel_down.ImpelDownSentenceType import ImpelDownSentenceType
from src.model.enums.impel_down.ImpelDownSource import ImpelDownSource
from src.model.pojo.Keyboard import Keyboard
from src.service.bounty_service import add_or_remove_bounty
from src.service.notification_service import send_notification


async def add_sentence(
    context: ContextTypes.DEFAULT_TYPE,
    user: User,
    sentence_type: ImpelDownSentenceType,
    bounty_action: ImpelDownBountyAction,
    release_date: datetime,
    reason: str,
    source: ImpelDownSource,
    external_id: int = None,
    should_send_notification: bool = True,
) -> None:
    """
    Save impel down status
    :param context: Telegram context
    :param user: User
    :param sentence_type: Sentence type
    :param bounty_action: Bounty action
    :param release_date: Release date
    :param reason: Reason
    :param source: Source
    :param external_id: External id
    :param should_send_notification: If a notification should be sent
    :return:
    """

    impel_down_log = ImpelDownLog()
    impel_down_log.user = user
    impel_down_log.sentence_type = sentence_type
    impel_down_log.bounty_action = bounty_action
    impel_down_log.previous_bounty = user.bounty
    impel_down_log.reason = reason
    impel_down_log.source = source
    impel_down_log.external_id = external_id

    user.impel_down_is_permanent = sentence_type is ImpelDownSentenceType.PERMANENT
    user.impel_down_release_date = (
        None
        if sentence_type in [ImpelDownSentenceType.NONE, ImpelDownSentenceType.PERMANENT]
        else release_date
    )
    impel_down_log.is_permanent = sentence_type is ImpelDownSentenceType.PERMANENT
    impel_down_log.release_date_time = user.impel_down_release_date

    if bounty_action is ImpelDownBountyAction.HALVE:
        user.bounty //= 2
    elif bounty_action is ImpelDownBountyAction.ERASE:
        user.bounty = 0

    impel_down_log.new_bounty = user.bounty

    if should_send_notification:
        notification = ImpelDownNotificationRestrictionPlaced(
            sentence_type, release_date, bounty_action, reason, impel_down_log
        )
        await send_notification(context, user, notification)

    impel_down_log.save()


async def post_bail(
    context: ContextTypes.DEFAULT_TYPE,
    update: Update,
    impel_down_log: ImpelDownLog,
    payer: User,
    should_save_payer: bool = False,
) -> None:
    """
    Post bail
    :param context: The context
    :param update: The update
    :param impel_down_log: The impel down log
    :param payer: The user posting bail
    :param should_save_payer: If the payer should be saved
    :return: None
    """

    bail = impel_down_log.get_bail()
    prisoner: User = impel_down_log.user

    # Remove from payer
    await add_or_remove_bounty(
        payer, bail, add=False, update=update, should_save=should_save_payer
    )

    prisoner.impel_down_release_date = datetime.now()
    impel_down_log.bail_payer = payer
    impel_down_log.bail_amount = bail
    impel_down_log.bail_date = datetime.now()

    # Send notification to the prisoner if they did not pay
    if prisoner != payer:
        await send_notification(
            context, prisoner, ImpelDownBailPostedNotification(impel_down_log), update=update
        )

    prisoner.save()
    impel_down_log.save()


def get_post_bail_deeplink_button(impel_down_log: ImpelDownLog) -> Keyboard | None:
    """
    Get the post bail deeplink
    :param impel_down_log: The impel down log
    :return: The deeplink
    """

    if impel_down_log is None:
        return None

    if impel_down_log.sentence_type != ImpelDownSentenceType.TEMPORARY:
        return None

    return Keyboard(
        text=phrases.KEY_POST_BAIL,
        info={ReservedKeyboardKeys.DEFAULT_PRIMARY_KEY: impel_down_log.user.id},
        screen=Screen.PVT_POST_BAIL,
        is_deeplink=True,
    )

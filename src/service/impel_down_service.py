from datetime import datetime

from telegram.ext import ContextTypes

from src.model.ImpelDownLog import ImpelDownLog
from src.model.User import User
from src.model.enums.Notification import ImpelDownNotificationRestrictionPlaced
from src.model.enums.impel_down.ImpelDownBountyAction import ImpelDownBountyAction
from src.model.enums.impel_down.ImpelDownSentenceOrigin import ImpelDownSentenceOrigin
from src.model.enums.impel_down.ImpelDownSentenceType import ImpelDownSentenceType
from src.service.notification_service import send_notification


async def add_sentence(
    context: ContextTypes.DEFAULT_TYPE,
    user: User,
    sentence_type: ImpelDownSentenceType,
    bounty_action: ImpelDownBountyAction,
    release_date: datetime,
    reason: str,
    origin: ImpelDownSentenceOrigin,
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
    :param origin: Origin
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
    impel_down_log.sentence_origin = origin
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
            sentence_type, release_date, bounty_action, reason
        )
        await send_notification(context, user, notification)

    impel_down_log.save()

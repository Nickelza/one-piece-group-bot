from datetime import datetime

from src.model.User import User
from src.model.enums.impel_down.ImpelDownBountyAction import ImpelDownBountyAction
from src.model.enums.impel_down.ImpelDownSentenceType import ImpelDownSentenceType
from src.model.tgrest.TgRest import TgRest
from src.model.tgrest.TgRestObjectType import TgRestObjectType


class TgRestImpelDownNotification(TgRest):
    """
    TgRestImpelDownNotification class is used to create a Telegram REST API request.
    """

    def __init__(self, bot_id: str, object_type: TgRestObjectType, user_id: int, sentence_type: ImpelDownSentenceType,
                 release_date_time: str, bounty_action: ImpelDownBountyAction, reason: str):
        """
        Constructor

        :param user_id: The user id
        :param sentence_type: The sentence type
        :param release_date_time: The release date time
        :param bounty_action: The bounty action
        :param reason: The reason
        """

        super().__init__(bot_id, object_type)

        self.user = User.get(User.id == user_id)
        self.sentence_type: ImpelDownSentenceType = ImpelDownSentenceType(sentence_type)
        self.release_date_time = datetime.strptime(release_date_time, '%Y-%m-%d %H:%M:%S')
        self.bounty_action: ImpelDownBountyAction = ImpelDownBountyAction(bounty_action)
        self.reason: str = reason

    def restriction_removed(self) -> bool:
        """
        Returns true if the restrictions are removed

        :return: True if the restrictions are removed
        """
        return self.sentence_type == ImpelDownSentenceType.NONE and self.bounty_action == ImpelDownBountyAction.NONE

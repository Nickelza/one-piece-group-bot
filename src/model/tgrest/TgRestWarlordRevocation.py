from src.model.User import User
from src.model.Warlord import Warlord
from src.model.tgrest.TgRest import TgRest
from src.model.tgrest.TgRestObjectType import TgRestObjectType


class TgRestWarlordRevocation(TgRest):
    """
    TgRestWarlordRevocation class is used to create a Telegram REST API request.
    """

    def __init__(self, bot_id: str, object_type: TgRestObjectType, user_id: int, warlord_id: int):
        """
        Constructor

        :param user_id: The user id
        :param warlord_id: The warlord id
        """

        super().__init__(bot_id, object_type)

        self.user: User = User.get_by_id(user_id)
        self.warlord: Warlord = Warlord.get_by_id(warlord_id)

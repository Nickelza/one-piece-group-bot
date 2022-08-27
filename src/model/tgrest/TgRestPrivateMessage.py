from src.model.tgrest.TgRest import TgRest
from src.model.tgrest.TgRestObjectType import TgRestObjectType


class TgRestPrivateMessage(TgRest):
    """
    TgRestPrivateMessage class is used to create a Telegram REST API requests for private messages
    """

    def __init__(self, bot_id: str, object_type: TgRestObjectType, tg_user_id: str, message: str):
        """
        Constructor
        :param tg_user_id: The telegram user id to send the message to
        :param message: The message
        """
        super().__init__(bot_id, object_type)

        self.tg_user_id: str = tg_user_id
        self.message: str = message

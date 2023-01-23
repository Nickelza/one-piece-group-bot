from src.model.DevilFruit import DevilFruit
from src.model.User import User
from src.model.tgrest.TgRest import TgRest
from src.model.tgrest.TgRestObjectType import TgRestObjectType


class TgRestDevilFruitAward(TgRest):
    """
    TgRestDevilFruitAward class is used to create a Telegram REST API request.
    """

    def __init__(self, bot_id: str, object_type: TgRestObjectType, user_id: int, devil_fruit_id: int, reason: str):
        """
        Constructor

        :param user_id: The user id
        :param devil_fruit_id: The devil fruit id
        :param reason: The reason why the devil fruit was awarded
        """

        super().__init__(bot_id, object_type)

        self.user_id: int = user_id
        self.user = User.get(User.id == user_id)
        self.devil_fruit = DevilFruit.get(DevilFruit.id == devil_fruit_id)
        self.reason: str = reason

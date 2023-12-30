from enum import StrEnum

from telegram import Update
from telegram.ext import ContextTypes

import constants as c
import resources.phrases as phrases
from src.model.GroupUser import GroupUser
from src.model.Prediction import Prediction
from src.model.PredictionOptionUser import PredictionOptionUser
from src.model.User import User
from src.model.enums.Emoji import Emoji
from src.model.enums.ListPage import ListPage
from src.model.enums.PredictionStatus import PredictionStatus
from src.model.enums.PredictionType import PredictionType
from src.model.enums.ReservedKeyboardKeys import ReservedKeyboardKeys
from src.model.enums.Screen import Screen
from src.model.pojo.Keyboard import Keyboard
from src.service.list_service import get_items_text_keyboard
from src.service.message_service import full_message_send, escape_valid_markdown_chars
from src.service.prediction_service import (
    get_user_prediction_status_emoji,
    get_prediction_text,
    get_user_prediction_status_text,
)


class PredictionReservedKeys(StrEnum):
    """
    The reserved keys for this screen
    """

    ITEM_ID = "a"


class PredictionListPage(ListPage):
    def __init__(self):
        """
        Constructor
        """

        super().__init__()

        self.object: Prediction = Prediction()

    def set_object(self, object_id: int) -> None:
        self.object = Prediction.get(Prediction.id == object_id)

    def get_items(self, page) -> list[Prediction]:
        """
        Get predictions that are open or closed/result set but user bet on them,
        or user created them,
        or they are of type user and are in sent status and
            (are public and creator is active in same group as user)
            or (user in same crew are creator)
        """
        return (
            self.get_select_items_statement()
            .order_by(Prediction.creation_date.desc(), Prediction.send_date.desc())
            .paginate(page, c.STANDARD_LIST_SIZE)
        )

    def get_total_items_count(self) -> int:
        return self.get_select_items_statement().count()

    def get_select_items_statement(self):
        return self.object.select().where(
            (
                (Prediction.status == PredictionStatus.SENT)
                & (Prediction.type != PredictionType.USER)
            )
            | (
                Prediction.status.in_([PredictionStatus.BETS_CLOSED, PredictionStatus.RESULT_SET])
                & (
                    Prediction.id.in_(
                        PredictionOptionUser.select(PredictionOptionUser.prediction).where(
                            PredictionOptionUser.user == self.user
                        )
                    )
                )
            )
            | (Prediction.creator == self.user)
            | (
                (Prediction.type == PredictionType.USER)
                & (Prediction.status == PredictionStatus.SENT)
                & (
                    (
                        (Prediction.is_public == True)
                        & (
                            GroupUser.get_user_is_active_is_same_group_statement(
                                self.user, Prediction.creator
                            )
                        )
                    )
                    | (self.user.get_in_same_crew_statement_condition(Prediction.creator))
                )
            )
        )

    def get_item_text(self) -> str:
        user_is_creator_emoji = Emoji.USER if self.object.creator == self.user else ""
        emoji = user_is_creator_emoji + get_user_prediction_status_emoji(self.object, self.user)
        return phrases.PREDICTION_ITEM_TEXT.format(
            emoji, escape_valid_markdown_chars(self.object.question)
        )

    def get_item_detail_text(self) -> str:
        return phrases.PREDICTION_ITEM_DETAIL_TEXT.format(
            get_prediction_text(self.object, add_bets_command=False, user=self.user),
            get_user_prediction_status_text(self.object, self.user, add_bets_command=False),
        )


async def manage(
    update: Update, context: ContextTypes.DEFAULT_TYPE, inbound_keyboard: Keyboard, user: User
) -> None:
    """
    Manage the prediction list screen
    :param update: The update
    :param context: The context
    :param inbound_keyboard: The inbound keyboard
    :param user: The user
    :return: None
    """

    prediction_list_page: PredictionListPage = PredictionListPage()
    prediction_list_page.user = user

    ot_text, items_keyboard = get_items_text_keyboard(
        inbound_keyboard,
        prediction_list_page,
        PredictionReservedKeys.ITEM_ID,
        Screen.PVT_PREDICTION_DETAIL,
        text_fill_in=phrases.PREDICTION_ITEM_TEXT_FILL_IN,
    )

    inline_keyboard: list[list[Keyboard]] = items_keyboard

    # Add the create prediction button
    inline_keyboard.append(
        [Keyboard(text=phrases.KEY_CREATE, screen=Screen.PVT_PREDICTION_CREATE)]
    )

    await full_message_send(
        context,
        ot_text,
        update=update,
        keyboard=inline_keyboard,
        inbound_keyboard=inbound_keyboard,
        excluded_keys_from_back_button=[ReservedKeyboardKeys.PAGE],
    )

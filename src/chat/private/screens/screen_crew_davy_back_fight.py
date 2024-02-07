from telegram import Update
from telegram.ext import ContextTypes

import resources.phrases as phrases
from src.model.Crew import Crew
from src.model.DavyBackFight import DavyBackFight
from src.model.User import User
from src.model.enums.Emoji import Emoji
from src.model.enums.GameStatus import GameStatus, GAME_STATUS_DESCRIPTIONS
from src.model.enums.ListPage import ListPage, EmojiLegend
from src.model.enums.ReservedKeyboardKeys import ReservedKeyboardKeys
from src.model.enums.Screen import Screen
from src.model.pojo.Keyboard import Keyboard
from src.service.crew_service import get_crew
from src.service.date_service import (
    get_remaining_duration,
    default_datetime_format,
)
from src.service.list_service import get_items_text_keyboard
from src.service.message_service import full_message_send


class CrewDavyBackFightListPage(ListPage):
    def __init__(self):
        """
        Constructor
        """

        super().__init__()

        self.object: DavyBackFight = DavyBackFight()
        self.crew: Crew = Crew()
        self.opponent_crew: Crew = Crew()
        self.is_challenger: bool = False
        self.effective_status: GameStatus = GameStatus.ND

    def set_object(self, object_id: int) -> None:
        self.object: DavyBackFight = DavyBackFight.get_by_id(object_id)
        self.crew = get_crew(self.user)
        self.is_challenger = self.object.challenger_crew == self.crew
        self.opponent_crew = (
            self.object.opponent_crew if self.is_challenger else self.object.challenger_crew
        )
        self.legend = self.get_emoji_legend()
        self.effective_status = self.legend.get_game_status()

    def get_items(self, page, limit=ListPage.DEFAULT_LIMIT) -> list[DavyBackFight]:
        return (
            self.object.select()
            .where(
                (
                    (DavyBackFight.challenger_crew == self.crew)
                    | (DavyBackFight.opponent_crew == self.crew)
                )
                & (DavyBackFight.status != GameStatus.FORCED_END)  # Rejected
                & (self.get_active_filter_list_condition())
            )
            .order_by(DavyBackFight.date.desc())
            .paginate(page, limit)
        )

    def get_item_text(self) -> str:
        return phrases.CREW_DAVY_BACK_FIGHT_ITEM_TEXT.format(
            self.legend.emoji, self.opponent_crew.get_name_with_deeplink(add_level=False)
        )

    def get_item_detail_text(self) -> str:
        super().get_item_detail_text()

        challenger_text = phrases.OPPONENT if self.is_challenger else phrases.CHALLENGER
        start_date = default_datetime_format(self.object.start_date, self.user)
        end_date = default_datetime_format(self.object.end_date, self.user)

        remaining_time_text = (
            phrases.DATETIME_REMAINING_PARENTHESIS.format(
                get_remaining_duration(self.object.end_date)
            )
            if self.effective_status is GameStatus.IN_PROGRESS
            else ""
        )

        status_text = phrases.LOG_ITEM_DETAIL_STATUS_TEXT.format(
            phrases.LOG_ITEM_DETAIL_GENERIC_OUTCOME_TEXT.format(
                self.legend.emoji, GAME_STATUS_DESCRIPTIONS[self.effective_status]
            )
        )

        return phrases.CREW_DAVY_BACK_FIGHT_ITEM_DETAIL_TEXT.format(
            challenger_text,
            self.opponent_crew.get_name_with_deeplink(add_level=False),
            start_date,
            end_date,
            remaining_time_text,
            self.object.participants_count,
            status_text,
        )

    def get_emoji_legend_list(self) -> list[EmojiLegend]:
        return [
            EmojiLegend(
                Emoji.LOG_POSITIVE,
                phrases.GAME_STATUS_WON,
                (
                    (
                        (DavyBackFight.challenger_crew == self.crew)
                        & (DavyBackFight.status == GameStatus.WON)
                    )
                    | (
                        (DavyBackFight.opponent_crew == self.crew)
                        & (DavyBackFight.status == GameStatus.LOST)
                    )
                ),
                status=GameStatus.WON,
            ),
            EmojiLegend(
                Emoji.LOG_NEGATIVE,
                phrases.GAME_STATUS_LOST,
                (
                    (
                        (DavyBackFight.opponent_crew == self.crew)
                        & (DavyBackFight.status == GameStatus.WON)
                    )
                    | (
                        (DavyBackFight.challenger_crew == self.crew)
                        & (DavyBackFight.status == GameStatus.LOST)
                    )
                ),
                status=GameStatus.LOST,
            ),
            EmojiLegend(
                Emoji.LOG_BLUE,
                phrases.GAME_STATUS_IN_PROGRESS,
                (DavyBackFight.status == GameStatus.IN_PROGRESS),
                status=GameStatus.IN_PROGRESS,
            ),
            EmojiLegend(
                Emoji.LOG_NEUTRAL,
                phrases.GAME_STATUS_COUNTDOWN_TO_START,
                (DavyBackFight.status == GameStatus.COUNTDOWN_TO_START),
                status=GameStatus.COUNTDOWN_TO_START,
            ),
        ]


async def manage(
    update: Update, context: ContextTypes.DEFAULT_TYPE, inbound_keyboard: Keyboard, user: User
) -> None:
    """
    Manage this screen
    :param update: The update object
    :param context: The context object
    :param user: The user object
    :param inbound_keyboard: The keyboard object
    :return: None
    """

    dbf_list_page: CrewDavyBackFightListPage = CrewDavyBackFightListPage()
    dbf_list_page.user = user
    dbf_list_page.crew = user.crew

    ot_text, items_keyboard = get_items_text_keyboard(
        inbound_keyboard,
        dbf_list_page,
        ReservedKeyboardKeys.DEFAULT_PRIMARY_KEY,
        Screen.PVT_CREW_DAVY_BACK_FIGHT_DETAIL,
        text_fill_in=phrases.CREW_DAVY_BACK_FIGHT_ITEM_TEXT_FILL_IN,
        context=context,
        user=user,
    )

    await full_message_send(
        context,
        ot_text,
        update=update,
        keyboard=items_keyboard,
        inbound_keyboard=inbound_keyboard,
        excluded_keys_from_back_button=[ReservedKeyboardKeys.PAGE],
    )

from telegram import Update
from telegram.ext import ContextTypes

import resources.phrases as phrases
from src.model.Crew import Crew
from src.model.DavyBackFight import DavyBackFight
from src.model.DavyBackFightParticipant import DavyBackFightParticipant
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
    datetime_is_after,
)
from src.service.list_service import get_items_text_keyboard
from src.service.message_service import full_message_send
from src.service.string_service import get_belly_formatted


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
            self.legend.emoji, self.opponent_crew.get_name_with_deeplink()
        )

    def get_item_detail_text(self) -> str:
        super().get_item_detail_text()

        challenger_text = phrases.OPPONENT if self.is_challenger else phrases.CHALLENGER
        start_date = default_datetime_format(
            self.object.start_date,
            self.user,
            add_remaining_time=(self.effective_status is GameStatus.COUNTDOWN_TO_START),
        )
        end_date = default_datetime_format(
            self.object.end_date,
            self.user,
        )

        # If in progress, show winning/losing/draw status
        display_status: GameStatus = self.effective_status
        if self.object.in_progress():
            display_status = self.object.get_in_progress_display_status(self.crew)

        contributions_text = ""
        if self.effective_status is not GameStatus.COUNTDOWN_TO_START:
            total_gained = self.object.get_crew_gain(self.crew)
            total_opponent_gained = self.object.get_crew_gain(self.opponent_crew)
            top_player: DavyBackFightParticipant = DavyBackFightParticipant.get_top_player(
                self.object, self.crew
            )
            contributions_text = phrases.CREW_DAVY_BACK_FIGHT_ITEM_DETAIL_CONTRIBUTIONS.format(
                get_belly_formatted(total_gained),
                get_belly_formatted(total_opponent_gained),
                top_player.user.get_markdown_mention(),
                top_player.get_contribution_formatted(),
            )

        end_text = ""
        if self.effective_status.is_finished():
            conscripted_member_text = ""

            if self.object.get_winner_crew() == self.crew:
                penalty_payout_text = (
                    phrases.CREW_DAVY_BACK_FIGHT_ITEM_DETAIL_PENALTY_RECEIVED.format(
                        self.object.get_penalty_payout_formatted()
                    )
                )
            else:
                penalty_payout_text = phrases.CREW_DAVY_BACK_FIGHT_ITEM_DETAIL_PENALTY_PAID.format(
                    self.object.get_penalty_payout_formatted()
                )

            if self.object.conscript is not None:
                conscripted_member_text = (
                    phrases.CREW_DAVY_BACK_FIGHT_ITEM_DETAIL_CONSCRIPTED_MEMBER.format(
                        self.object.conscript.get_markdown_mention()
                    )
                )
            end_text = phrases.CREW_DAVY_BACK_FIGHT_ITEM_DETAIL_END.format(
                default_datetime_format(self.object.penalty_end_date),
                penalty_payout_text,
                conscripted_member_text,
            )

            # Add penalty rules
            if datetime_is_after(self.object.penalty_end_date):
                penalty_remaining = get_remaining_duration(self.object.penalty_end_date)
                if self.crew == self.object.get_winner_crew():
                    end_text += phrases.CREW_DAVY_BACK_FIGHT_WON.format(penalty_remaining)
                else:
                    end_text += phrases.CREW_DAVY_BACK_FIGHT_LOST.format(penalty_remaining)
        else:
            if self.object.in_progress():
                # Pending chest
                contributions_text += (
                    phrases.CREW_DAVY_BACK_FIGHT_ITEM_DETAIL_PENDING_CHEST.format(
                        get_belly_formatted(self.object.get_chest_amount(self.crew))
                    )
                )

            # Add rules
            end_text += phrases.CREW_DAVY_BACK_FIGHT_PARTICIPANTS_RULES_WITH_TIME.format(
                self.object.get_remaining_time()
            )

        status_text = phrases.LOG_ITEM_DETAIL_STATUS_TEXT.format(
            phrases.LOG_ITEM_DETAIL_GENERIC_OUTCOME_TEXT_NO_BOLD.format(
                display_status.get_log_emoji(), GAME_STATUS_DESCRIPTIONS[display_status]
            )
        )

        return phrases.CREW_DAVY_BACK_FIGHT_ITEM_DETAIL_TEXT.format(
            challenger_text,
            self.opponent_crew.get_name_with_deeplink(),
            start_date,
            end_date,
            self.object.participants_count,
            contributions_text,
            status_text,
            end_text,
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

    def get_direct_item(self) -> DavyBackFight | None:
        """
        Get active DavyBackFight
        """
        # If they have only one DBF, return that
        all_items = self.get_items(1)
        if len(all_items) == 1:
            return all_items[0]

        # If they have an active DBF, return that
        active_dbf: DavyBackFight = self.crew.get_active_davy_back_fight()
        if active_dbf:
            return active_dbf

        # If they have a penalty DBF, return that
        penalty_dbf: DavyBackFight = self.crew.get_penalty_davy_back_fight()
        if penalty_dbf:
            return penalty_dbf

        return None


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
    from src.chat.private.screens.screen_crew_davy_back_fight_detail import (
        manage as manage_davy_back_fight_detail,
    )

    dbf_list_page: CrewDavyBackFightListPage = CrewDavyBackFightListPage()
    dbf_list_page.user = user
    dbf_list_page.crew = get_crew(user)

    if not (
        ReservedKeyboardKeys.DIRECT_ITEM in inbound_keyboard.info
        and not inbound_keyboard.get_bool(ReservedKeyboardKeys.DIRECT_ITEM)
    ):
        # Has active DBF, go directly there
        direct_item: DavyBackFight = dbf_list_page.get_direct_item()
        if direct_item is not None:
            inbound_keyboard.info[ReservedKeyboardKeys.DEFAULT_PRIMARY_KEY] = direct_item.id
            inbound_keyboard.info[ReservedKeyboardKeys.DIRECT_ITEM] = True
            await manage_davy_back_fight_detail(update, context, inbound_keyboard, user)
            return

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
        excluded_keys_from_back_button=[
            ReservedKeyboardKeys.PAGE,
            ReservedKeyboardKeys.DIRECT_ITEM,
        ],
    )

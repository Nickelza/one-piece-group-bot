from telegram import Update
from telegram.ext import ContextTypes

import resources.phrases as phrases
from src.model.Crew import Crew
from src.model.CrewMemberChestContribution import CrewMemberChestContribution
from src.model.User import User
from src.model.enums.ListPage import ListPage
from src.model.enums.ReservedKeyboardKeys import ReservedKeyboardKeys
from src.model.enums.Screen import Screen
from src.model.pojo.Keyboard import Keyboard
from src.service.crew_service import get_crew
from src.service.date_service import default_date_format
from src.service.list_service import get_items_text_keyboard
from src.service.message_service import full_message_send, mention_markdown_user
from src.service.string_service import get_belly_formatted


class CrewMemberListPage(ListPage):
    def __init__(self):
        """
        Constructor
        """

        super().__init__()

        self.object: User = User()  # Current member
        self.crew: Crew = Crew()  # Crew of the current member

    def set_object(self, object_id: int) -> None:
        self.object = User.get_by_id(object_id)
        self.crew = get_crew(self.object, validate_against_crew=self.user.crew)

    def get_items(self, page, limit=ListPage.DEFAULT_LIMIT) -> list[User]:
        return self.crew.get_members(limit=limit, page=page)

    def get_item_text(self) -> str:
        ot_text = phrases.CREW_MEMBER_ITEM_TEXT.format(mention_markdown_user(self.object))
        if self.object.crew_role is None:
            return ot_text

        return ot_text + phrases.CREW_MEMBER_ITEM_ROLE.format(
            self.object.get_crew_role_description()
        )

    def get_item_detail_text(self) -> str:
        super().get_item_detail_text()

        member: User = self.object
        crew: Crew = self.crew

        # Get join date and relative order
        crew_members = crew.get_members()  # Already ordered by join date
        member_join_order = list(crew_members).index(member) + 1

        # Get chest contribution and relative order
        chest_contributions = crew.get_chest_contributions()  # Already ordered by contribution
        member_contribution = CrewMemberChestContribution.get_or_none(
            (CrewMemberChestContribution.crew == crew)
            & (CrewMemberChestContribution.user == member)
        )
        member_contribution_amount = 0
        if member_contribution is None:
            member_chest_order = len(chest_contributions) + 1
        else:
            member_contribution_amount = member_contribution.amount
            member_chest_order = list(chest_contributions).index(member_contribution) + 1

        ot_text = phrases.CREW_MEMBER_ITEM_DETAIL.format(
            member.get_markdown_mention(),
            member.get_bounty_formatted(),
            default_date_format(member.crew_join_date, member),
            member_join_order,
            get_belly_formatted(member_contribution_amount),
            member_chest_order,
            (phrases.TEXT_YES if member.has_crew_mvp_bonus() else phrases.TEXT_NO),
        )

        return ot_text


async def manage(
    update: Update, context: ContextTypes.DEFAULT_TYPE, inbound_keyboard: Keyboard, user: User
) -> None:
    """
    Manage the Crew member screen
    :param update: The update object
    :param context: The context object
    :param user: The user object
    :param inbound_keyboard: The keyboard object
    :return: None
    """

    crew_member_list_page: CrewMemberListPage = CrewMemberListPage()
    crew_member_list_page.user = user
    crew_member_list_page.crew = user.crew

    ot_text, items_keyboard = get_items_text_keyboard(
        inbound_keyboard,
        crew_member_list_page,
        ReservedKeyboardKeys.DEFAULT_PRIMARY_KEY,
        Screen.PVT_CREW_MEMBER_DETAIL,
        text_fill_in=phrases.CREW_MEMBER_ITEM_TEXT_FILL_IN,
    )

    await full_message_send(
        context,
        ot_text,
        update=update,
        keyboard=items_keyboard,
        inbound_keyboard=inbound_keyboard,
        excluded_keys_from_back_button=[ReservedKeyboardKeys.PAGE],
    )

from enum import StrEnum

from resources import phrases
from src.model.enums.LogType import LogType
from src.model.enums.ReservedKeyboardKeys import ReservedKeyboardKeys
from src.model.enums.Screen import Screen


class BountyLoanSource(StrEnum):
    USER = "user"
    PLUNDER = "plunder"

    def get_description(self) -> str:
        return DESCRIPTIONS[self]

    def get_deeplink(self, item_id: int) -> str:
        from src.model.enums.Log import Log
        from src.service.message_service import get_deeplink

        if self in DEEPLINK_LOG_TYPES:
            return Log.get_deeplink_by_type(DEEPLINK_LOG_TYPES[self], item_id)

        return get_deeplink(
            {ReservedKeyboardKeys.DEFAULT_PRIMARY_KEY: item_id}, screen=DEEPLINK_SCREENS[self]
        )


DESCRIPTIONS = {
    BountyLoanSource.USER: phrases.BOUNTY_LOAN_SOURCE_USER,
    BountyLoanSource.PLUNDER: phrases.BOUNTY_LOAN_SOURCE_PLUNDER,
}

DEEPLINK_SCREENS = {
    BountyLoanSource.USER: Screen.PVT_BOUNTY_LOAN_DETAIL,  # Should never happen
}

DEEPLINK_LOG_TYPES = {
    BountyLoanSource.PLUNDER: LogType.PLUNDER,
}

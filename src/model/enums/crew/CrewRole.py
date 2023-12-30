from enum import IntEnum

import resources.phrases as phrases


class CrewRole(IntEnum):
    """
    Enum class for Crew Roles
    """

    CAPTAIN = 1
    FIRST_MATE = 2

    def get_description(self) -> str:
        """
        Returns the description of the Crew Role
        :return: The description of the Crew Role
        """

        return CREW_ROLE_NAME_MAP[self]


CREW_ROLE_NAME_MAP = {
    CrewRole.CAPTAIN: phrases.CREW_ROLE_CAPTAIN,
    CrewRole.FIRST_MATE: phrases.CREW_ROLE_FIRST_MATE,
}

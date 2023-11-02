from enum import IntEnum


class CrewRole(IntEnum):
    """
    Enum class for Crew Roles
    """
    CAPTAIN = 1

    def get_description(self) -> str:
        """
        Returns the description of the Crew Role
        :return: The description of the Crew Role
        """

        return CREW_ROLE_NAME_MAP[self]


CREW_ROLE_NAME_MAP = {
    CrewRole.CAPTAIN: "Captain"
}

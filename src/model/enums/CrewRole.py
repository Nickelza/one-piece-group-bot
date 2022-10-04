from enum import IntEnum


class CrewRole(IntEnum):
    """
    Enum class for Crew Roles
    """
    CAPTAIN = 1


CREW_ROLE_NAME_MAP = {
    CrewRole.CAPTAIN: "Captain"
}

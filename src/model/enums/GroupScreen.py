from enum import Enum

from src.model.enums.Command import Command


class GroupScreen(Enum):
    UNKNOWN = 0
    USER_STATUS = 1
    DOC_Q_GAME = 2
    CHANGE_REGION = 3

    # Deprecated
    SHOW_BOUNTY = -1


COMMAND_TO_GROUP_SCREEN = {
    Command.GRP_USER_STATUS: GroupScreen.USER_STATUS,
    Command.GRP_DOC_Q_GAME: GroupScreen.DOC_Q_GAME,
    Command.GRP_CHANGE_REGION_NEW_WORLD: GroupScreen.CHANGE_REGION,
    Command.GRP_CHANGE_REGION_PARADISE: GroupScreen.CHANGE_REGION,
    Command.GRP_SHOW_BOUNTY: GroupScreen.SHOW_BOUNTY
}

import resources.Environment as Env
import src.model.enums.Location as Location
from src.model.enums.Screen import Screen


def get_formatted_from_string(string: str):
    """
    Returns the command formatted for the text display.
    """
    return '`/{}`'.format(string)


class Command:
    """
    Class for Commands
    """

    def __init__(self, name: str, screen: Screen, active: bool = True, replaced_by: str = None,
                 only_in_reply: bool = False, allow_self_reply: bool = False, allow_reply_to_bot: bool = False,
                 required_location: Location.Location = None):
        self.name = name
        self.active = active
        self.replaced_by = replaced_by
        self.only_in_reply = only_in_reply
        self.allow_self_reply = allow_self_reply
        self.allow_reply_to_bot = allow_reply_to_bot
        self.screen = screen
        self.required_location = required_location
        self.parameters = []

    def get_formatted(self):
        """
        Returns the command formatted for the text display.
        """
        return get_formatted_from_string(self.name)

    def get_replaced_by_formatted(self):
        """
        Returns the command formatted for the text display.
        """
        return get_formatted_from_string(self.replaced_by)


ND = None

PVT_START = Command('start', Screen.PVT_START)
GRP_DOC_Q_GAME = Command('docq', Screen.GRP_DOC_Q_GAME, required_location=Location.get_by_level(
    Env.REQUIRED_LOCATION_LEVEL_DOCQ.get_int()))
GRP_USER_STATUS = Command('status', Screen.GRP_USER_STATUS)
GRP_CHANGE_REGION_NEW_WORLD = Command('newworld', Screen.GRP_CHANGE_REGION,
                                      required_location=Location.get_last_paradise())
GRP_CHANGE_REGION_PARADISE = Command('paradise', Screen.GRP_CHANGE_REGION,
                                     required_location=Location.get_last_paradise())
GRP_FIGHT = Command('fight', Screen.GRP_FIGHT, only_in_reply=True, required_location=Location.get_first_new_world())
GRP_SHOW_BOUNTY = Command('bounty', Screen.GRP_SHOW_BOUNTY, active=False, replaced_by='status')
GRP_GAME = Command('challenge', Screen.GRP_GAME, only_in_reply=True, required_location=Location.get_first_new_world())

ADM_SAVE_MEDIA = Command('savemedia', Screen.ADM_SAVE_MEDIA, allow_self_reply=True, allow_reply_to_bot=True)

COMMANDS = [ND, PVT_START, GRP_DOC_Q_GAME, GRP_USER_STATUS, GRP_CHANGE_REGION_NEW_WORLD,
            GRP_CHANGE_REGION_PARADISE, GRP_FIGHT, GRP_SHOW_BOUNTY, ADM_SAVE_MEDIA, GRP_GAME]


def get_by_name(name: str):
    """
    Returns the Command object with the given name.
    """
    for command in COMMANDS:
        if command is not None and command.name == name:
            return command

    raise ValueError('Command not found: {}'.format(name))


def get_by_screen(screen: Screen):
    """
    Returns the Command object with the given screen.
    """
    for command in COMMANDS:
        if command is not None and command.screen == screen:
            return command

    raise ValueError('Command not found: {}'.format(screen))

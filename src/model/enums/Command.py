import resources.Environment as Env
import src.model.enums.Location as Location
from src.model.enums.CommandName import CommandName
from src.model.enums.Feature import Feature
from src.model.enums.MessageSource import MessageSource
from src.model.enums.Screen import (
    Screen,
    ONLY_BY_CAPTAIN_OR_FIRST_MATE,
    ALLOW_WHILE_ARRESTED,
    ALLOW_WHILE_ARRESTED_TEMPORARY,
    ALLOW_DEEPLINK,
    DEPRECATED,
    ONLY_BY_CAPTAIN,
)


class Command:
    """
    Class for Commands
    """

    def __init__(
        self,
        name: CommandName | None,
        screen: Screen,
        active: bool = True,
        replaced_by: CommandName = None,
        only_in_reply: bool = False,
        allow_self_reply: bool = False,
        allow_reply_to_bot: bool = False,
        allow_while_arrested: bool = False,
        allow_while_arrested_temporary: bool = False,
        required_location: Location.Location = None,
        parameters: list = None,
        message_source: MessageSource = MessageSource.ND,
        only_by_crew_captain: bool = False,
        only_in_reply_to_crew_member: bool = False,
        only_by_boss: bool = False,
        allow_reply_to_arrested: bool = False,
        answer_callback: bool = False,
        show_alert: bool = True,
        only_by_chat_admin: bool = False,
        send_message_if_error: bool = True,
        feature: Feature = None,
        allow_deeplink: bool = False,
        only_by_crew_captain_or_first_mate: bool = False,
        only_by_crew_captain_or_first_mate_keyboard: bool = True,
    ):
        """
        Constructor
        :param name: The name of the command
        :param screen: The screen the command is used in
        :param active: True if the command is active
        :param replaced_by: The command that replaces this command
        :param only_in_reply: True if the command can only be used in reply to a message
        :param allow_self_reply: True if the command can be used in reply to a message sent by the
        user
        :param allow_reply_to_bot: True if the command can be used in reply to a message sent by
        the bot
        :param allow_while_arrested: True if the command can be used while the user is arrested
        :param allow_while_arrested_temporary: True if the command can be used while the user is
        arrested temporarily
        :param required_location: The location required to use the command
        :param parameters: The parameters of the command
        :param message_source: The source of the message
        :param only_by_crew_captain: True if the command can only be used by a Crew Captain
        :param only_in_reply_to_crew_member: True if the command can only be used in reply to a
        Crew Member. Automatically sets only_in_reply to True if True
        :param only_by_boss: True if the command can only be used by a boss
        :param allow_reply_to_arrested: True if the command can be used in reply to a message sent
        by an arrested user
        :param answer_callback: True if the command should answer the callback query in case of
        error instead of editing the message
        :param show_alert: True if the command should show an alert when answering the callback
        query in case of error
        :param only_by_chat_admin: True if the command can only be used by a chat admin
        :param send_message_if_error: True if a message should be sent if the command isn't
        authorized
        :param feature: The feature the command belongs to. If provided, the command will only be
        allowed in chats that have the feature enabled
        :param allow_deeplink: Allow accessing the command screen via deeplink
        :param only_by_crew_captain_or_first_mate: True if the command can only be used by a
        Crew Captain or First Mate
        :param only_by_crew_captain_or_first_mate_keyboard: True if the command can only be used
        by a Crew Captain or First Mate via keyboard
        """
        self.name = name
        self.active = active
        self.replaced_by = replaced_by
        self.only_in_reply = only_in_reply
        self.allow_self_reply = allow_self_reply
        self.allow_reply_to_bot = allow_reply_to_bot
        self.allow_while_arrested = allow_while_arrested
        self.allow_while_arrested_temporary = allow_while_arrested_temporary
        self.screen = screen
        self.required_location = required_location
        self.parameters: list[str] = [] if parameters is None else parameters
        self.message_source: MessageSource = message_source
        self.only_by_crew_captain = only_by_crew_captain
        self.only_in_reply_to_crew_member = only_in_reply_to_crew_member
        self.only_by_boss = only_by_boss
        self.allow_reply_to_arrested = allow_reply_to_arrested
        self.answer_callback = answer_callback
        self.show_alert = show_alert
        self.only_by_chat_admin = only_by_chat_admin
        self.send_message_if_error = send_message_if_error
        self.feature = feature
        self.allow_deeplink = allow_deeplink
        self.only_by_crew_captain_or_first_mate = only_by_crew_captain_or_first_mate
        self.only_by_crew_captain_or_first_mate_keyboard = (
            only_by_crew_captain_or_first_mate_keyboard
        )

        if only_in_reply_to_crew_member and not only_in_reply:
            self.only_in_reply = True

    def get_formatted(self):
        """
        Returns the command formatted for the text display.
        """
        return self.name.get_formatted()

    def get_replaced_by_formatted(self):
        """
        Returns the command formatted for the text display.
        """
        return self.replaced_by.get_formatted()

    def __eq__(self, other):
        """
        Overrides the default implementation
        """

        if isinstance(other, Command):
            return self.name == other.name and self.screen == other.screen

        return False


COMMANDS = []

ND = None
COMMANDS.append(ND)

PVT_START = Command(CommandName.START, Screen.PVT_START, allow_while_arrested=True)
COMMANDS.append(PVT_START)

PVT_USER_STATUS = Command(CommandName.STATUS, Screen.PVT_USER_STATUS, allow_while_arrested=True)
COMMANDS.append(PVT_USER_STATUS)

# Merge all lists with limitations
limitations_list = set(
    DEPRECATED
    + ALLOW_WHILE_ARRESTED
    + ALLOW_WHILE_ARRESTED_TEMPORARY
    + ALLOW_DEEPLINK
    + ONLY_BY_CAPTAIN_OR_FIRST_MATE
    + ONLY_BY_CAPTAIN
)
for sc in limitations_list:
    _active = sc not in DEPRECATED
    _allow_while_arrested = sc in ALLOW_WHILE_ARRESTED
    _allow_while_arrested_temporary = sc in ALLOW_WHILE_ARRESTED_TEMPORARY
    _allow_deeplink = sc in ALLOW_DEEPLINK
    _only_by_crew_captain_or_first_mate = sc in ONLY_BY_CAPTAIN_OR_FIRST_MATE
    _only_by_crew_captain = sc in ONLY_BY_CAPTAIN

    COMMANDS.append(
        Command(
            CommandName.EMPTY,
            sc,
            active=_active,
            allow_while_arrested=_allow_while_arrested,
            allow_while_arrested_temporary=_allow_while_arrested_temporary,
            allow_deeplink=_allow_deeplink,
            only_by_crew_captain_or_first_mate=_only_by_crew_captain_or_first_mate,
            only_by_crew_captain=_only_by_crew_captain,
        )
    )

# To set required location
PVT_LOGS_TYPE_STATS = Command(
    CommandName.EMPTY,
    Screen.PVT_LOGS_TYPE_STATS,
    required_location=Location.get_by_level(Env.REQUIRED_LOCATION_LEVEL_LOG_STATS.get_int()),
)
COMMANDS.append(PVT_LOGS_TYPE_STATS)

PVT_PREDICTION_CREATE = Command(
    CommandName.EMPTY,
    Screen.PVT_PREDICTION_CREATE,
    required_location=Location.get_by_level(
        Env.REQUIRED_LOCATION_LEVEL_PREDICTION_CREATE.get_int()
    ),
)
COMMANDS.append(PVT_PREDICTION_CREATE)

GRP_GAME_OPPONENT_CONFIRMATION = Command(
    CommandName.EMPTY,
    Screen.GRP_GAME_OPPONENT_CONFIRMATION,
    answer_callback=True,
    required_location=Location.get_by_level(Env.REQUIRED_LOCATION_LEVEL_GAME.get_int()),
)

GRP_DOC_Q_GAME = Command(
    CommandName.DOC_Q,
    Screen.GRP_DOC_Q_GAME,
    required_location=Location.get_by_level(Env.REQUIRED_LOCATION_LEVEL_DOC_Q_GAME.get_int()),
    feature=Feature.DOC_Q,
)
COMMANDS.append(GRP_DOC_Q_GAME)

GRP_USER_STATUS = Command(
    CommandName.STATUS,
    Screen.GRP_USER_STATUS,
    allow_while_arrested=True,
    allow_reply_to_arrested=True,
    feature=Feature.STATUS,
)
COMMANDS.append(GRP_USER_STATUS)

GRP_CHANGE_REGION_NEW_WORLD = Command(
    CommandName.NEW_WORLD, Screen.GRP_CHANGE_REGION, required_location=Location.get_last_paradise()
)
COMMANDS.append(GRP_CHANGE_REGION_NEW_WORLD)

GRP_CHANGE_REGION_PARADISE = Command(
    CommandName.PARADISE, Screen.GRP_CHANGE_REGION, required_location=Location.get_last_paradise()
)
COMMANDS.append(GRP_CHANGE_REGION_PARADISE)

GRP_FIGHT = Command(
    CommandName.FIGHT,
    Screen.GRP_FIGHT,
    only_in_reply=True,
    feature=Feature.FIGHT,
    required_location=Location.get_by_level(Env.REQUIRED_LOCATION_LEVEL_FIGHT.get_int()),
)
COMMANDS.append(GRP_FIGHT)

GRP_GAME = Command(
    CommandName.GAME,
    Screen.GRP_GAME,
    feature=Feature.CHALLENGE,
    required_location=Location.get_by_level(Env.REQUIRED_LOCATION_LEVEL_GAME.get_int()),
)
COMMANDS.append(GRP_GAME)

GRP_PREDICTION_BET = Command(
    CommandName.PREDICTION_BET,
    Screen.GRP_PREDICTION_BET,
    only_in_reply=True,
    required_location=Location.get_by_level(Env.REQUIRED_LOCATION_LEVEL_PREDICTION_BET.get_int()),
    allow_reply_to_bot=True,
)
COMMANDS.append(GRP_PREDICTION_BET)

GRP_PREDICTION_BET_REMOVE = Command(
    CommandName.PREDICTION_BET_REMOVE,
    Screen.GRP_PREDICTION_BET_REMOVE,
    only_in_reply=True,
    allow_reply_to_bot=True,
)
COMMANDS.append(GRP_PREDICTION_BET_REMOVE)

GRP_PREDICTION_BET_STATUS = Command(
    CommandName.PREDICTION_BET_STATUS,
    Screen.GRP_PREDICTION_BET_STATUS,
    only_in_reply=True,
    allow_reply_to_bot=True,
)
COMMANDS.append(GRP_PREDICTION_BET_STATUS)

GRP_CREW_JOIN = Command(
    CommandName.CREW_JOIN,
    Screen.GRP_CREW_JOIN,
    only_in_reply_to_crew_member=True,
    feature=Feature.CREW,
)
COMMANDS.append(GRP_CREW_JOIN)

GRP_CREW_INVITE = Command(
    CommandName.CREW_INVITE,
    Screen.GRP_CREW_INVITE,
    only_in_reply=True,
    feature=Feature.CREW,
    only_by_crew_captain_or_first_mate=True,
    only_by_crew_captain_or_first_mate_keyboard=False,
)
COMMANDS.append(GRP_CREW_INVITE)

GRP_SILENCE = Command(
    CommandName.SILENCE, Screen.GRP_SILENCE, only_by_boss=True, feature=Feature.SILENCE
)
COMMANDS.append(GRP_SILENCE)

GRP_SILENCE_END = Command(
    CommandName.SILENCE_END, Screen.GRP_SILENCE_END, only_by_boss=True, feature=Feature.SILENCE
)
COMMANDS.append(GRP_SILENCE_END)

GRP_SPEAK = Command(
    CommandName.SPEAK,
    Screen.GRP_SPEAK,
    only_by_boss=True,
    only_in_reply=True,
    feature=Feature.SILENCE,
)
COMMANDS.append(GRP_SPEAK)

GRP_BOUNTY_GIFT = Command(
    CommandName.BOUNTY_GIFT,
    Screen.GRP_BOUNTY_GIFT,
    only_in_reply=True,
    feature=Feature.BOUNTY_GIFT,
)
COMMANDS.append(GRP_BOUNTY_GIFT)

GRP_BOUNTY_LOAN = Command(
    CommandName.BOUNTY_LOAN,
    Screen.GRP_BOUNTY_LOAN,
    only_in_reply=True,
    feature=Feature.BOUNTY_LOAN,
)
COMMANDS.append(GRP_BOUNTY_LOAN)

GRP_DEVIL_FRUIT_SELL = Command(
    CommandName.DEVIL_FRUIT_SELL, Screen.GRP_DEVIL_FRUIT_SELL, feature=Feature.DEVIL_FRUIT_SELL
)
COMMANDS.append(GRP_DEVIL_FRUIT_SELL)

GRP_PLUNDER = Command(
    CommandName.PLUNDER,
    Screen.GRP_PLUNDER,
    only_in_reply=True,
    feature=Feature.PLUNDER,
    required_location=Location.get_by_level(Env.REQUIRED_LOCATION_LEVEL_PLUNDER.get_int()),
)
COMMANDS.append(GRP_PLUNDER)

GRP_SETTINGS = Command(
    CommandName.SETTINGS,
    Screen.GRP_SETTINGS,
    allow_while_arrested=True,
    only_by_chat_admin=True,
    answer_callback=True,
    send_message_if_error=False,
)
COMMANDS.append(GRP_SETTINGS)

GRP_DAILY_REWARD = Command(
    CommandName.DAILY_REWARD,
    Screen.GRP_DAILY_REWARD,
    feature=Feature.DAILY_REWARD,
    allow_while_arrested_temporary=True,
)
COMMANDS.append(GRP_DAILY_REWARD)


def get_by_name(name: str, message_source: MessageSource = MessageSource.ND):
    """
    Returns the Command object with the given name.
    """
    for command in COMMANDS:
        if command is not None and command.name.lower() == name.lower():
            if message_source is not MessageSource.ND:
                if command.screen[0] == message_source[0]:
                    return command
            else:
                return command

    raise ValueError("Command not found: {}".format(name))


def get_by_screen(screen: Screen):
    """
    Returns the Command object with the given screen.
    """
    for command in COMMANDS:
        if command is not None and command.screen is screen:
            return command

    raise ValueError("Command not found: {}".format(screen))

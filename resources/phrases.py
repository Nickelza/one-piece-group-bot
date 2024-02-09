import resources.Environment as Env
from src.model.enums.CommandName import CommandName
from src.model.enums.Emoji import Emoji


def surround_with_arrows(text: str) -> str:
    """
    Surround the text with left and right arrows
    :param text: The text
    :return: The text surrounded with left and right arrows
    """
    return Emoji.RIGHT_ARROW + text + Emoji.LEFT_ARROW


ANTI_SPAM_WARNING = "Too many messages sent, please slow down..."

COMMAND_NOT_IN_REPLY_ERROR = "This command can only be used in a reply to a message"
COMMAND_IN_REPLY_TO_BOT_ERROR = "This command can't be used in reply to a bot"
COMMAND_IN_REPLY_TO_ERROR = "This command can't be used in a reply to your own message"
COMMAND_NOT_ACTIVE_ERROR = "This command is no longer available"
COMMAND_NOT_ACTIVE_WITH_REPLACEMENT_ERROR = (
    COMMAND_NOT_ACTIVE_ERROR + ". " + "Please Use {} instead"
)
COMMAND_FOR_NEW_WORLD_USERS_ERROR = "This command is only available for users in the New World"
COMMAND_FOR_USERS_AFTER_LOCATION_ERROR = (
    "This command is only available for users who have reached *{}*.\n\nCurrent location: *{}*"
)
COMMAND_FOR_USERS_AFTER_LOCATION_ERROR_JOIN_CREW = (
    "\n\n_Join a Crew to quickly level up your location!_"
)
COMMAND_WHILE_ARRESTED_ERROR = "This command is not available while you are arrested"
COMMAND_ONLY_BY_CREW_CAPTAIN_ERROR = "This command is only available to Crew Captains"
COMMAND_ONLY_BY_CREW_CAPTAIN_OR_FIRST_MATE_ERROR = (
    "This command is only available to Crew Captains and First Mates"
)
COMMAND_NOT_IN_REPLY_TO_CREW_MEMBER_ERROR = (
    "This command can only be used in reply to a message from a Crew Member"
)
COMMAND_ONLY_BY_BOSS_ERROR = (
    "This command can only be used by an Admin, the Pirate King or a Legendary Pirate"
)
COMMAND_IN_REPLY_TO_ARRESTED_ERROR = (
    "This command can't be used in reply to a message from an arrested user"
)
COMMAND_ONLY_BY_CHAT_ADMIN_ERROR = "This command can only be used by a chat admin"
COMMAND_FEATURE_DISABLED_ERROR = (
    "This feature is currently disabled in this {}.\nYou can ask an Admin to enable via"
    f" {CommandName.SETTINGS.get_formatted()}"
)
COMMAND_NOT_ALLOWED_FROM_DEEPLINK_ERROR = "This command is not allowed from a deeplink"

SHOW_USER_STATUS = "User: {}\nBounty: ฿*{}*{}\nRank: {}\nLocation: {}"
SHOW_USER_STATUS_FROZEN_BOUNTY = " \\(Frozen\\)"
SHOW_USER_STATUS_RANK_PRISONER = Emoji.PRISONER + " Prisoner"
SHOW_USER_STATUS_IMPEL_DOWN = "Impel Down"
SHOW_USER_STATUS_PENDING_BOUNTY = "\nPending bounty: ฿*{}*"
SHOW_USER_STATUS_REMAINING_SENTENCE = "\nRemaining sentence: {}"
SHOW_USER_STATUS_PERMANENT_IMPEL_DOWN = "Permanent"
SHOW_USER_STATUS_FIGHT_IMMUNITY = "\nFight immunity: {}"
SHOW_USER_STATUS_FIGHT_COOLDOWN = "\nFight cooldown: {}"
SHOW_USER_STATUS_PLUNDER_IMMUNITY = "\nPlunder immunity: {}"
SHOW_USER_STATUS_PLUNDER_COOLDOWN = "\nPlunder cooldown: {}"
SHOW_USER_STATUS_WARLORD_REMAINING_TIME = "\nWarlord remaining time: {}"
SHOW_USER_STATUS_CREW = "\nCrew: {}"
SHOW_USER_STATUS_BOUNTY_DAILY_BONUSES_TITLE = "\n\n*Daily Bounty Bonus*"
SHOW_USER_STATUS_BOUNTY_BONUSES_TEXT = "\n{}{} \\({}%\\)"
SHOW_USER_STATUS_BOUNTY_BONUS_CREW = "Crew"
SHOW_USER_STATUS_BOUNTY_BONUS_CREW_MVP = "Crew MVP"
SHOW_USER_STATUS_BOUNTY_BONUS_NEW_WORLD = "New World"
SHOW_USER_STATUS_BOUNTY_DEDUCTIONS_TITLE = "\n\n*Bounty Deductions*"
SHOW_USER_STATUS_EXPIRED_LOAN = "Expired loan"
SHOW_USER_STATUS_INCOME_TAX = "Income tax"
SHOW_USER_STATUS_ADD_REPLY = "_Requested by {}_"
SHOW_USER_STATUS_DEVIL_FRUIT = "\n\n*Devil Fruit*\n_{}_{}"
SHOW_USER_STATUS_CREW_ABILITIES = "\n\n*Crew Abilities*{}"
NOT_ALLOWED_TO_VIEW_REPLIED_STATUS = (
    "You can only view the status of those who rank below you.\n\n{} rank: {}\n{} rank: {}"
)
ROOKIE_STATUS_PRIVATE_CHAT_ONLY = "Rookies can only view their status in Private Chat"
PRISONER_STATUS_PRIVATE_CHAT_ONLY = "Prisoners can only view their status in Private Chat"
STATUS_PRIVATE_CHAT_KEY = "View in Private Chat"
BOUNTY_RESET = "Bounties have been reset"

LEADERBOARD = (
    "*{}* Leaderboard for week *{}* of *{}*\n\nHere are the top {} users with the most"
    " bounties:{}{}{}\n\n_Next bounty reset on {} \\(in {}\\)_"
)
LEADERBOARD_ROW = "\n\n{}°: {}\n{} - ฿*{}*"
LEADERBOARD_LOCAL = "Local"
LEADERBOARD_GLOBAL = "Global"
LEADERBOARD_VIEW_GLOBAL_LEADERBOARD = "\n\n\n" + Emoji.GLOBE + "[Global Leaderboard]({})"
LEADERBOARD_WARLORDS = "\n\n\n" + Emoji.LEADERBOARD_WARLORD + " *Warlords*"
LEADERBOARD_WARLORD_ROW = "\n• [{}]({})"
LEADERBOARD_RANK_PIRATE_KING = "Pirate King"
LEADERBOARD_RANK_EMPEROR = "Emperor"
LEADERBOARD_RANK_FIRST_MATE = "First Mate"
LEADERBOARD_RANK_SUPERNOVA = "Supernova"
LEADERBOARD_RANK_ROOKIE = "Rookie"
LEADERBOARD_RANK_ADMIN = "Veteran"
LEADERBOARD_RANK_LEGENDARY_PIRATE = "Legendary Pirate"
LEADERBOARD_RANK_WARLORD = "Warlord"


SAVE_MEDIA_NOT_IN_REPLY_TO_MEDIA = "This command can only be used in a reply to a media message"
SAVED_MEDIA_UNKNOWN_TYPE = "Unknown media type. Available types are: *{}*"
SAVE_MEDIA_SUCCESS = "Media saved as *{}*"

GAME_WIN_LOSE_STATUS = (
    "_Current bounty: ฿*{}*_\n_Final bounty if you win: ฿*{}*_\n_Final bounty if you lose: ฿*{}*_"
)
GAME_WIN_STATUS = "_You won ฿*{}*!_\n_Current bounty: ฿*{}*_"
GAME_LOSE_STATUS = "_You lost ฿*{}*!_\n_Current bounty: ฿*{}*_"

DOC_Q_GAME_NOT_ENOUGH_BOUNTY = (
    "You need a bounty of at least ฿*{}* to summon Doc Q.\n\n_Current bounty: ฿*{}*_"
)
DOC_Q_GAME_LIMIT_REACHED = "You have reached the limit of Doc Q games. You can play again in *{}*"
DOC_Q_GAME_START = (
    "Hi {}, allow me to offer you an apple.\nIf you choose the right one, you will win ฿*{}*, else"
    " you will lose ฿*{}*.\nChoose wisely!"
    + "\n\n"
    + GAME_WIN_LOSE_STATUS
)

DOC_Q_GAME_NOT_FOUND = "Doc Q game not found"
DOC_Q_GAME_CANCEL = "See you next time!"
DOC_Q_GAME_WIN = (
    "You're...haha...cough! cough! a really lucky one {}.\nLet's go, Stronger...agh..!"
    + "\n\n{}"
    + GAME_WIN_STATUS
)
DOC_Q_GAME_LOSE = (
    "Seems like today wasn't your lucky day {}...cough!...only the *{}°* apple wasn't rigged"
    " haha...\nDon't be so reckless or you won't survive long in these treacherous seas!\nLet's"
    " go, Stronger...agh..!"
    + "\n\n{}"
    + GAME_LOSE_STATUS
)

# Error messages
USER_NOT_FOUND = "User not found"
UNRECOGNIZED_SCREEN = "Unrecognized command"
SAVED_MEDIA_NOT_FOUND = "Saved Media not found"
UNKNOWN_EXTRA_STEP = "Unknown extra step"
PRIVATE_STEP_NOT_SET = "Private step not set"
SAVED_USER_DATA_NOT_FOUND = "Saved user data not found"

# Keyboard options
KEYBOARD_OPTION_CANCEL = Emoji.CANCEL + " Cancel"
KEYBOARD_OPTION_DELETE = Emoji.DELETE + " Delete"
KEYBOARD_OPTION_CLOSE = Emoji.CLOSE + " Close"
KEYBOARD_OPTION_ACCEPT = Emoji.ACCEPT + " Accept"
KEYBOARD_OPTION_REJECT = Emoji.REJECT + " Reject"
KEYBOARD_OPTION_FIGHT = Emoji.FIGHT + " Fight"
KEYBOARD_OPTION_PLUNDER = Emoji.PLUNDER + " Plunder"
KEYBOARD_OPTION_RETREAT = Emoji.RETREAT + " Retreat"
KEYBOARD_OPTION_BACK = Emoji.BACK + " Back"
KEYBOARD_OPTION_YES = Emoji.YES + " Yes"
KEYBOARD_OPTION_NO = Emoji.NO + " No"

TEXT_YES = "Yes"
TEXT_NO = "No"
TEXT_WON = "won"
TEXT_LOST = "lost"
TEXT_IT_WAS = "it was"
TEXT_THEY_WERE = "they were"
TEXT_FROM = "from"
TEXT_TO = "to"
TEXT_TOPIC = "Topic"
TEXT_GROUP = "Group"
TEXT_NOT_SET = "Not set"
TEXT_RANDOM = "Random"
TEXT_ONLY = "Only {}"
TEXT_YOU = "You"
TEXT_STOLE = "stole"
TEXT_OWE = "[owe]({})"

EXCEPTION_CHAT_ID_NOT_PROVIDED = "chat_id is None and update.effective_chat.id is None"
EXCEPTION_NO_EDIT_MESSAGE = "new_message is False but update.callback_query is None"

KEYBOARD_NOT_FOUND = "Keyboard not found"
KEYBOARD_USE_UNAUTHORIZED = "You are not authorized to use this keyboard"

LOCATION_CHANGE_REGION_PROPOSAL = "{}{} would you like to move to {}?"
LOCATION_CHANGE_REGION_PROPOSAL_REJECTED = "{}{} You can move to {} later with {} command"
LOCATION_NEW_WORLD_REQUEST_REJECTED_NOT_ENOUGH_BOUNTY = (
    "You need a bounty of at least ฿*{}* to move to the New World."
)
LOCATION_ALREADY_IN_REGION = "You are already in {}"
LOCATION_CANNOT_CHANGE_REGION = "You can change region in *{}*"
LOCATION_INVALID_CHANGE_REGION_REQUEST = "Invalid region"

CHALLENGER = "Challenger"
OPPONENT = "Opponent"
SENDER = "Sender"
RECEIVER = "Receiver"

FIGHT_NOT_FOUND = "Fight not found"
FIGHT_OPPONENT_NOT_FOUND = "Opponent not found"
FIGHT_CANNOT_FIGHT_USER = "You can't fight this user"
FIGHT_CANNOT_FIGHT_CREW_MEMBER = "You can't fight a member of your Crew"
FIGHT_USER_IN_COOLDOWN = "Fight cooldown active. You can initiate a fight in *{}*"
FIGHT_CONFIRMATION_ODDS_RECALCULATED = (
    "\n_*\\(Probability recalculated with opponent's Crew average bounty\\)*_"
)
FIGHT_CONFIRMATION_REQUEST = (
    "{} are you sure you want to fight {}?\nI predict a {}% probability of {}."
    + "{}\n\n"
    + GAME_WIN_LOSE_STATUS
)
FIGHT_CONFIRMATION_OUTCOME_VICTORY = "victory"
FIGHT_CONFIRMATION_OUTCOME_DEFEAT = "defeat"
FIGHT_WIN = (
    "Just as I foresaw, {} won the fight against {}.\nI don't need the cards to tell me that your"
    " strength is incredible..."
    + "\n\n"
    + GAME_WIN_STATUS
)
FIGHT_LOSE = (
    "Just as I foresaw, {} lost the fight against {}.\nLooks like your luck ran out..."
    + "\n\n"
    + GAME_LOSE_STATUS
)
FIGHT_CONFIRMATION_RETREAT = "You have successfully retreated"

ENABLED = Emoji.ENABLED + " Enabled"
DISABLED = Emoji.DISABLED + " Disabled"
CURRENT_SETTING = "Current setting: {}"

INLINE_QUERY_SEND_ITEM = "Send item"

# General
KEY_MANAGE = "Manage"
KEY_VIEW = "View"
KEY_CREATE = Emoji.CREATE + " Create"
KEY_SAVE = Emoji.SAVE + " Save"
KEY_ENABLE = Emoji.ENABLED + " Enable"
KEY_DISABLE = Emoji.DISABLED + " Disable"
KEY_OPEN = "Open"
KEY_CLOSE = Emoji.CLOSE + " Close"
KEY_SHARE = Emoji.SHARE + " Share"
KEY_SEND_TO_GROUP = Emoji.GROUP + " Send to group"
KEY_SET_RESULT = "Set result"
KEY_CONFIRM = "Confirm"
KEY_MODIFY = "Modify"
KEY_RESET = "Reset"

# Private chat
PVT_TXT_START = (
    f"Welcome to One Piece Group Bot, a Bot that brings the Bounty System to any Chat Group!\nWhat"
    f" would you like to do?"
)
PVT_KEY_SETTINGS = Emoji.SETTINGS + " Settings"
PVT_KEY_STATUS = Emoji.STATUS + " Status"
PVT_TXT_SETTINGS = "Which setting would you like to change?"
PVT_KEY_SETTINGS_LOCATION_UPDATE = "Location update"
PVT_TXT_SETTINGS_LOCATION_UPDATE = (
    "Do you want to receive an update when you move to a new location?"
)
PVT_KEY_CREW = Emoji.CREW + " Crew"
PVT_KEY_CREW_MEMBERS = "Members"
PVT_KEY_CREW_MEMBER_VIEW = "View member"
PVT_KEY_CREW_LEAVE = "Leave"
PVT_KEY_CREW_SEARCH = Emoji.SEARCH + " Search"
PVT_KEY_CREW_SEARCH_JOIN = "Join"
PVT_KEY_CREW_EDIT_NAME = "Name"
PVT_KEY_CREW_EDIT_DESCRIPTION = "Description"
PVT_KEY_CREW_EDIT_REQUIRED_BOUNTY = "Required bounty"
PVT_KEY_CREW_DISBAND = Emoji.DELETE + " Disband"
PVT_KEY_CREW_MEMBER_REMOVE = "Expel"
PVT_KEY_CREW_MEMBER_FIRST_MATE_PROMOTE = "Promote to First Mate"
PVT_KEY_CREW_MEMBER_FIRST_MATE_DEMOTE = "Demote from First Mate"
PVT_KEY_CREW_MEMBER_POST_BAIL = "Post bail"
PVT_KEY_CREW_ABILITY = "Abilities"
PVT_KEY_CREW_ABILITY_ACTIVATE = "Activate"
PVT_KEY_CREW_ABILITY_RANDOM = Emoji.DICE + " Random"
PVT_KEY_CREW_POWERUP = "Power-up"
PVT_KEY_CREW_LEVEL = "Level"
PVT_KEY_CREW_LEVEL_UP = "Level up"
PVT_KEY_CREW_ALLOW_VIEW_IN_SEARCH = "{} Allow search"
PVT_KEY_CREW_ALLOW_JOIN_FROM_SEARCH = "{} Allow join"
PVT_KEY_CREW_DAVY_BACK_FIGHT = Emoji.FIGHT + " Davy Back Fight"
PVT_KEY_CREW_DAVY_BACK_FIGHT_PARTICIPANT_SELECT = "Choose players"
PVT_KEY_CREW_DAVY_BACK_FIGHT_PARTICIPANT_VIEW = "Players"
PVT_KEY_SETTINGS_NOTIFICATIONS = "Notifications"
PVT_TXT_SETTINGS_NOTIFICATIONS = "Which category of notifications would you like to change?"
PVT_TXT_SETTINGS_NOTIFICATIONS_TYPE = "Which notification would you like to change?"
PVT_KEY_MANAGE_NOTIFICATION_SETTINGS = "Manage notification settings"
PVT_KEY_SETTINGS_TIMEZONE = "Time zone"
PVT_TXT_SETTINGS_TIMEZONE = (
    "\nCurrent time: *{}*\nCurrent timezone: *{}* \\({}\\)\n\nTo set a new time zone, send a"
    " location name \\(city, region, state or country\\)"
)
PVT_TXT_SETTINGS_TIMEZONE_INVALID = (
    "Invalid location. Please send a correct location name \\(city, region, state or country\\)"
)
PVT_KEY_SETTINGS_TIMEZONE_RESET = "Reset"
PVT_TXT_SETTINGS_TIMEZONE_UNKNOWN = "Default - " + Env.TZ.get()

PVT_KEY_LOGS = Emoji.LOGS + " Logs"
PVT_TXT_LOGS = "Which log would you like to view?"
PVT_KEY_LOGS_STATS = Emoji.STATS + " Stats"
PVT_KEY_PREVIOUS_PAGE = Emoji.LEFT_ARROW
PVT_KEY_NEXT_PAGE = Emoji.RIGHT_ARROW
PVT_KEY_PREDICTION = Emoji.PREDICTION + " Predictions"
PVT_KEY_PREDICTION_DETAIL_PLACE_BET = "Place bet"
PVT_KEY_PREDICTION_DETAIL_REMOVE_BET = "Remove bet"
PVT_KEY_PREDICTION_DETAIL_EDIT = "Edit"
PVT_KEY_PREDICTION_CREATE_ALLOW_MULTIPLE_CHOICES = "Allow multiple choices"
PVT_KEY_PREDICTION_CREATE_ALLOW_BET_WITHDRAWAL = "Allow bet withdrawal"
PVT_KEY_PREDICTION_CREATE_IS_PUBLIC = "Public"
PVT_KEY_PREDICTION_CREATE_SET_CLOSE_DATE = Emoji.PREDICTION_CLOSED + " Set closing date"
PVT_KEY_PREDICTION_CREATE_REMOVE_CLOSE_DATE = Emoji.PREDICTION_CLOSED + " Remove closing date"
PVT_KEY_PREDICTION_CREATE_SET_CUT_OFF_DATE = Emoji.PREDICTION_CUT_OFF + " Set cut-off date"
PVT_KEY_PREDICTION_CHANGE_POLL = Emoji.CHANGE + " Change poll"
PVT_KEY_PREDICTION_NO_CORRECT_OPTION = "No correct option"
PVT_KEY_DEVIL_FRUIT = Emoji.DEVIL_FRUIT + " Devil Fruit"
PVT_KEY_DEVIL_FRUIT_DETAIL_EAT = "Eat"
PVT_KEY_DEVIL_FRUIT_DETAIL_TRADE = "Trade"
PVT_KEY_DEVIL_FRUIT_DETAIL_DISCARD = "Discard"
PVT_KEY_GO_TO_MESSAGE = "Go to message"
PVT_KEY_VIEW = "View"
PVT_KEY_BOUNTY_LOAN = Emoji.MONEY + " Loan"
PVT_KEY_BOUNTY_LOAN_DETAIL_PAY = "Pay"
PVT_KEY_BOUNTY_LOAN_DETAIL_FORGIVE = "Forgive"
PVT_KEY_BOUNTY_LOAN_DETAIL_PAY_ALL = "Pay all"
PVT_KEY_STRING_FILTER_REMOVE = "Remove {} filter"
PVT_KEY_SHOW_ALL = "Back to list"

GRP_KEY_DEVIL_FRUIT_BUY = Emoji.MONEY + " Buy"
GRP_TXT_SETTINGS = "{}Which Bounty System features would you like to enable in this {}?"
GRP_KEY_GO_TO_MESSAGE = "Go to message"
GRP_KEY_PREDICTION_BET_IN_PRIVATE_CHAT = "Bet in private chat"
GRP_KEY_PREDICTION_VIEW_IN_PRIVATE_CHAT = "View in private chat"
GRP_KEY_GAME_PLAY = "Play"

DATETIME_EXAMPLES = """
Write the date using this format:
dd/mm/yy hh:mm

*Examples*:
• 1/4/2022 22:30
• in 10 days 5 hours 2 minutes
• Tomorrow at 12:00

Current time: *{}*
Current time zone: *{}* \\({}\\)
[Change time zone]({})
""".strip()

DATETIME_EXAMPLES_NO_DURATION = """
Write the date using this format:
dd/mm/yy hh:mm

*Examples*:
• 1/4/2022 22:30
• 10 hours ago
• Yesterday at 12:00

Current time: *{}*
Current time zone: *{}* \\({}\\)
[Change time zone]({})
""".strip()

DATETIME_REMAINING = "{} remaining"
DATETIME_REMAINING_PARENTHESIS = f" _\\({DATETIME_REMAINING}\\)_"

ITEM_LINK = "[{}]({})"

ACTION_INSUFFICIENT_BOUNTY = "Insufficient bounty, you need at least ฿*{}*"
ACTION_WAGER_LESS_THAN_MIN = "The minimum amount is ฿*{}*"
ACTION_INVALID_WAGER_AMOUNT = (
    "Invalid amount. Make sure it is a number with only '.' or ',' as decimal separator or with a"
    " valid magnitude.\n\nExample: \n- 10.000.000 or 10,000,000\n- 10k, 10thousand, 10m,"
    " 10million, 10b, 10billion"
)
ACTION_INVALID_DURATION = (
    "Invalid duration. Make sure it is a number with only '.' or ',' as decimal separator or with"
    " a valid unit.\n\nExample: \n - 1min, 1h, 1d, 1week"
)

SYSTEM_UPDATE = (
    Emoji.CONFETTI + "New update" + Emoji.CONFETTI + "\n\n*{}*\n\n{}\n\n[View full changelog]({})"
)

GAME_CANNOT_CHALLENGE_USER = "You can't challenge this user"
GAME_CHOOSE_GAME = "Which game would you like to play?"
GAME_NO_WAGER_AMOUNT = (
    "You need to specify a wager amount.\n\nExample:"
    f" {CommandName.GAME.get_formatted()} 10.000.000"
)

GAME_NOT_FOUND = "Game not found"
GAME_REQUEST = (
    "{}, you have been challenged by {} to play *{}* with a wager of"
    " ฿*{}*.\n\n_*Description*: {}_\n\nWould you like to accept?\n\nIf the challenge is not"
    f" accepted within {Env.GAME_CONFIRMATION_TIMEOUT.get_int()} seconds, it will be automatically"
    " rejected."
)
GAME_REQUEST_OPEN = (
    "{} is challenging anyone to play *{}* with a wager of ฿*{}*.\n\nPress the button below"
    " to accept.\n\nIf the challenge is not accepted within"
    f" {Env.GAME_CONFIRMATION_TIMEOUT.get_int()} seconds, it will be automatically rejected."
)
GAME_CANCELED = "Game cancelled"
GAME_CHALLENGE_REJECTED = "{} has rejected the challenge"
GAME_INVALID = "Invalid game"
GAME_NOT_SELECTED_NAME = "Not selected"
GAME_TEXT = "*{}*\n\n_*Description*: {}_\n\n{} vs {}\nWager: ฿*{}*{}\n\n{}"
GAME_STATUS_AWAITING_CHOICE = "Status: Awaiting choice"
GAME_STATUS_AWAITING_USER_CHOICE = "Status: Awaiting {}'s choice"
GAME_RESULT_DRAW = "Result: Draw"
GAME_RESULT_WIN = Emoji.WINNER + " {} won"
GAME_NOT_YOUR_TURN = "It's not your turn"
GAME_TURN = "Status: {}'s turn"
GAME_ENDED = "This game has ended"
GAME_CANNOT_INITIATE = (
    "Challenge limit reached, make sure you have canceled any pending challenges.\nYou can"
    " initiate another challenge in *{}*, but in the meantime you can ask another user to"
    " challenge you."
)
GAME_PENDING_KEY = "Pending challenge"
GAME_FORCED_END = (
    "This game has ended due to bounty reset or inactivity. The wagers has been returned to the"
    " players."
)

GAME_STATUS_ND = "Not defined"
GAME_STATUS_IN_PROGRESS = "In progress"
GAME_STATUS_WON = "Won"
GAME_STATUS_LOST = "Lost"
GAME_STATUS_DRAW = "Draw"
GAME_STATUS_AWAITING_SELECTION = "Awaiting game selection"
GAME_STATUS_AWAITING_OPPONENT_CONFIRMATION = "Awaiting opponent confirmation"
GAME_STATUS_FORCED_END = "Forced end due to bounty reset"
GAME_STATUS_COUNTDOWN_TO_START = "Countdown to start"
GAME_STATUS_WINNING = "Winning"
GAME_STATUS_LOSING = "Losing"
GAME_COUNTDOWN = "The game will start in *{}*"
GAME_STARTED = "Game in progress"
GAME_TIMEOUT = (
    "This game was canceled due to timeout while awaiting opponent confirmation.\n\nThe wager has"
    " been returned to the challenger."
)
GAME_INPUT_NOT_PLAYER = "You are not a player of this game"
GAME_INPUT_GAME_FINISHED = "This game has ended"
GAME_INPUT_COUNTDOWN = (
    "The game has not started yet.\nStay on this chat as to not miss the first message!"
)
GAME_RESULT_CHARACTER = "Character: {}"
GAME_RESULT_TERM = "Word: {}"
GAME_DIFFICULTY = "\nDifficulty: {}"
GAME_DIFFICULTY_EASY = "Easy"
GAME_DIFFICULTY_MEDIUM = "Medium"
GAME_DIFFICULTY_HARD = "Hard"

ROCK_PAPER_SCISSORS_GAME_NAME = "Rock Paper Scissors"
ROCK_PAPER_SCISSORS_GAME_DESCRIPTION = (
    "Try to beat your opponent by choosing rock, paper or scissors. \nRock beats scissors,"
    " scissors beats paper and paper beats rock."
)
ROCK_PAPER_SCISSORS_CHOICE_ALERT = "You chose {}"
ROCK_PAPER_SCISSORS_CHOICE_ROCK = Emoji.ROCK + " Rock"
ROCK_PAPER_SCISSORS_CHOICE_PAPER = Emoji.PAPER + " Paper"
ROCK_PAPER_SCISSORS_CHOICE_SCISSORS = Emoji.SCISSORS + " Scissors"
ROCK_PAPER_SCISSORS_CHOICES = "{} chose {} \n{} chose {}\n\n"

RUSSIAN_ROULETTE_GAME_NAME = "Russian Roulette"
RUSSIAN_ROULETTE_GAME_DESCRIPTION = "Try to avoid choosing the chamber with the bullet."

RUSSIAN_ROULETTE_GAME_CHAMBER_ALREADY_FIRED = (
    "This chamber has already been fired. Choose another one."
)
RUSSIAN_ROULETTE_GAME_BULLET_SHOT = "You've died"
RUSSIAN_ROULETTE_GAME_BULLET_NOT_SHOT = "You've survived another round"

GUESS_GAME_INPUT_CAPTION_HINT = "\n\n" + Emoji.NEW + "Hint: {}"
GUESS_GAME_INPUT_CAPTION_SECONDS_TO_NEXT_HINT = "\n\nIn *{}* seconds, a hint will be sent"
GUESS_GAME_INPUT_CAPTION_SECONDS_TO_NEXT_IMAGE = (
    "\n\nIn *{}* seconds, an easier variation will be sent"
)
GUESS_GAME_INPUT_CAPTION_SECONDS_TO_NEXT_LIFE_1 = "In *{}* seconds, a new life will be issued"
GUESS_GAME_INPUT_CAPTION_SECONDS_TO_NEXT_LIFE_2 = "A new life will be issued every {} seconds"
GUESS_GAME_INPUT_CAPTION_SECONDS_TO_NEXT_DETAIL = "\n\nIn *{}* seconds, a new detail will be given"

GUESS_CHARACTER_GAME_INPUT_CAPTION = (
    "Send your guesses as text messages, you will be notified if you are correct. \nThe name must"
    f" be the same as the one used on [One Piece Wiki]({Env.ONE_PIECE_WIKI_URL.get()})"
)
GUESS_TERM_GAME_INPUT_CAPTION = (
    "Send your guesses as text messages, you will be notified if you are correct. \nThe term must"
    f" be the same as the one used on [One Piece Wiki]({Env.ONE_PIECE_WIKI_URL.get()})"
)
GUESS_GAME_CORRECT_ANSWER = f"Congratulations, you guessed correctly{Emoji.CONFETTI}\n\n{{}}"
GUESS_GAME_OPPONENT_CORRECT_ANSWER = (
    f"Oops, your opponent was able to guess before you😔\nBetter luck next time!\n\n{{}}"
)

WHOS_WHO_GAME_NAME = "Who's Who"
WHOS_WHO_GAME_DESCRIPTION = (
    "Guess the blurred character. \nEvery {} seconds, a less blurred image will be sent until the"
    " character is fully revealed.\nThis game is played in private chat with the Bot."
)

SHAMBLES_GAME_NAME = "Shambles"
SHAMBLES_GAME_DESCRIPTION = (
    "Guess the One Piece related word from a crossword puzzle. \nEvery {} seconds, an extra letter"
    " will be removed from the puzzle making it easier to guess.\nThis game is played in private"
    " chat with the Bot."
)

GUESS_OR_LIFE_GAME_NAME = "Guess or Life"
GUESS_OR_LIFE_GAME_DESCRIPTION = (
    "Guess the missing letters of the One Piece related word, any wrong guess will cost a life.\nA"
    " new life will be issued every {} seconds."
)
GUESS_OR_LIFE_GAME_CORRECT_LETTER = f"{Emoji.CORRECT} Correct letter!"
GUESS_OR_LIFE_GAME_WRONG_LETTER = f"{Emoji.LOG_NEGATIVE} Wrong letter"
GUESS_OR_LIFE_GAME_WORD_LIVES = "{}{}\nLives: {}{}"
GUESS_OR_LIFE_GAME_NAME_WORD = "*{}*\n{}"
GUESS_OR_LIFE_GAME_NAME_WORD_LIVES = "*{}*\n" + GUESS_OR_LIFE_GAME_WORD_LIVES
GUESS_OR_LIFE_GAME_REMAINING_USED_LETTERS = "\n\nRemaining letters: {}\n\nUsed letters: {}"
GUESS_OR_LIFE_GAME_PRIVATE_RECAP = "{}\n\n{}"

PUNK_RECORDS_GAME_NAME = "Punk Records"
PUNK_RECORDS_GAME_DESCRIPTION = (
    "Guess the One Piece related character from details about them. \nEvery {} seconds, a new"
    " detail will be revealed making it easier to guess.\nThis game is played in private chat with"
    " the Bot."
)
PUNK_RECORDS_GAME_RECAP = "{}{}"
PUNK_RECORDS_GAME_RECAP_DETAIL = "\n{}*{}*: {}"
PUNK_RECORDS_GAME_RECAP_DETAIL_LIST = "\n*{}*\n{}"

PREDICTION_NOT_FOUND = "Prediction not found"
PREDICTION_NOT_IN_NEW_STATUS = "Prediction not in NEW status"
PREDICTION_NOT_SENT = "Prediction not sent"
PREDICTION_NOT_IN_SENT_STATUS = "Prediction not in SENT status"
PREDICTION_NOT_IN_BETS_CLOSED_STATUS = "Prediction not in BETS\\_CLOSED status"
UNKNOWN_PREDICTION_ACTION = "Unknown prediction action"
PREDICTION_TEXT = "*{}*\n{}\n\n*Total wager*: ฿{}\n*Status*: {}{}{}{}{}"
PREDICTION_CREATE_RECAP = "*{}*\n{}{}"
PREDICTION_TEXT_OPTION = "\n{}. {}"
PREDICTION_TEXT_OPTION_WITH_PERCENTAGE = PREDICTION_TEXT_OPTION + " \\(*{}%*\\){}"
PREDICTION_CLOSING_DATE = "\n*Closing date*: {}"
PREDICTION_CUT_OFF_DATE = "\n*Cut off date*: {}"
PREDICTION_WAGERS_REFUNDED = "\n{} Wagers refunded{}"
PREDICTION_WAGERS_REFUNDED_MAX = " \\(max. ฿{}\\)"
PREDICTION_MULTIPLE_BETS_ALLOWED = "\n{} Multiple bets allowed"
PREDICTION_MULTIPLE_BETS_ALLOWED_DESCRIPTION = "\n_\\(Users can bet on multiple options\\)_"
PREDICTION_CAN_WITHDRAW_BETS = "\n{} Can withdraw bets"
PREDICTION_CAN_WITHDRAW_BETS_DESCRIPTION = (
    "\n_\\(Users can withdraw their bets before the prediction is closed\\)_"
)
PREDICTION_IS_PUBLIC = "\n{} Public"
PREDICTION_IS_PUBLIC_DESCRIPTION = (
    "\n_\\(Anyone in your groups can find this prediction.\nIf disabled, only those who you share"
    " the prediction with can view it.\nYour fellow Crew members will always be able to find"
    " it._\\)"
)
PREDICTION_BET_INVALID_FORMAT = (
    "Make sure your bet is in the following"
    f" format:\n{CommandName.PREDICTION_BET.get_formatted()} <amount> <option number>\n\nExample:"
    f" {CommandName.PREDICTION_BET.get_formatted()} 10.000.000 1"
)
PREDICTION_BET_HOW_TO_PLACE_BET = (
    "\n\n_To place a bet, reply to this message with the following"
    f" command:\n{CommandName.PREDICTION_BET.get_formatted()} <amount> <option number>\nExample:"
    f" {CommandName.PREDICTION_BET.get_formatted()} 10.000.000 1_"
)
PREDICTION_BET_HOW_TO_REMOVE_BET = (
    "\n\n_To remove a bet, reply to the prediction with the following"
    f" command:\n{CommandName.PREDICTION_BET_REMOVE.get_formatted()} <option number>\nExample:"
    f" {CommandName.PREDICTION_BET_REMOVE.get_formatted()} 1_"
)
PREDICTION_BET_HOW_TO_REMOVE_ALL_BETS = (
    "\n\n_To remove all bets, reply to the prediction with the following"
    f" command:\n{CommandName.PREDICTION_BET_REMOVE.get_formatted()}_"
)
PREDICTION_BET_HOW_TO_VIEW_BET_STATUS = (
    "\n\n_To view your bet status, reply to the prediction with the following"
    f" command:\n{CommandName.PREDICTION_BET_STATUS.get_formatted()}_"
)

PREDICTION_CLOSED_FOR_BETS = "This prediction no longer accept bets"
PREDICTION_NOT_FOUND_IN_REPLY = (
    "Prediction not found in replied message. Make sure you replied to a prediction or the"
    " prediction might have been deleted."
)
PREDICTION_ALREADY_BET = "You have already bet on this prediction"
PREDICTION_ALREADY_BET_ON_OPTION = "You have already bet on this option"
PREDICTION_OPTION_NOT_FOUND = "Option *{}* not found in prediction"
PREDICTION_BET_SUCCESS = "Bet placed successfully"
PREDICTION_RESULTS_SET = "The results of this prediction have been set"
PREDICTION_BET_REMOVE_INVALID_FORMAT = (
    "Make sure your command is in the following"
    f" format:\n{CommandName.PREDICTION_BET_REMOVE.get_formatted()} ]<option number>\n\nExample:"
    f" {CommandName.PREDICTION_BET_REMOVE.get_formatted()} 1"
)
PREDICTION_BET_REMOVE_SUCCESS = "Bet removed successfully"
PREDICTION_BET_USER_HAS_NOT_BET = "You have not bet on this prediction"
PREDICTION_BET_REMOVE_ALL_SUCCESS = (
    "All your bets on this prediction have been removed successfully"
)
PREDICTION_CLOSED_FOR_BETS_REMOVAL = "You can no longer withdraw bets from this prediction"
PREDICTION_DOES_NOT_ACCEPT_BETS_WITHDRAWAL = "This prediction does not accept bets withdrawal"
PREDICTION_OPTION_NOT_BET_ON = "You have not bet on this option"
PREDICTION_STATUS_BETS_HEADER = "*Bets*"
PREDICTION_STATUS_OPTION = "\n\n*{}*. {} \n*Amount*: ฿{}"
PREDICTION_STATUS_POTENTIAL_WIN = "\n*Potential win*: ฿{}"
PREDICTION_STATUS_RESULT_LOST = "\n*Result*: " + Emoji.PREDICTION_BET_LOSE + "Lost"
PREDICTION_STATUS_RESULT_LOSS_REFUNDED = " \\(Refunded\\)"
PREDICTION_STATUS_RESULT_WIN = "\n*Result*: " + Emoji.PREDICTION_BET_WIN + "฿{}"
PREDICTION_STATUS_TOTAL_WIN = "\n\n*Total win*: " + Emoji.PREDICTION_BET_WIN + "฿{}"
PREDICTION_STATUS_NET_WIN = "\n\n*Net win*: " + Emoji.PREDICTION_BET_WIN + "฿{}"
PREDICTION_STATUS_TOTAL_LOSS = "\n\n*Total loss*: " + Emoji.PREDICTION_BET_LOSE + "฿{}"
PREDICTION_STATUS_NET_LOSS = "\n\n*Net loss*: " + Emoji.PREDICTION_BET_LOSE + "฿{}"
PREDICTION_ALL_BETS_REMOVED_FOR_BOUNTY_RESET = (
    "All bets have been removed from this prediction due to bounty reset"
)
# Prediction Private Chat
PREDICTION_ITEM_TEXT = "{} {}"
PREDICTION_ITEM_TEXT_FILL_IN = "Prediction"
PREDICTION_ITEM_DETAIL_TEXT = "{}\n\n{}"
PREDICTION_PLACE_BET_TEXT = "{}"
PREDICTION_PLACE_BET_DETAIL_TEXT = (
    "*Question*: {}\n\n*Option*: {}\n\n_Please send the amount you want to bet_"
)
PREDICTION_PLACE_BET_LIST_OVERVIEW = "On which option do you want to place a bet?\n{}"
PREDICTION_REMOVE_BET_TEXT = "{}"
PREDICTION_REMOVE_BET_LIST_OVERVIEW = "From which option do you want to remove your bet?\n{}"
PREDICTION_CREATE_COOLDOWN_ACTIVE = "You can create a prediction in *{}*"
PREDICTION_CREATE_REQUEST_POLL = (
    "Send the prediction as a Telegram poll with the question and options"
)
PREDICTION_CREATE_INVALID_POLL = (
    "Invalid poll. Make sure to send a Telegram poll with a question and at least two options"
)
PREDICTION_CAN_EDIT_POLL_ONLY_IF_NEW = (
    "You can only edit the question and options if the prediction if the prediction has not been"
    " enabled yet"
)
PREDICTION_CREATE_REQUEST_CLOSE_DATE = (
    "Send the closing date of the prediction.\n\n" + DATETIME_EXAMPLES
)
PREDICTION_CREATE_INVALID_CLOSE_DATE = (
    "Invalid closing date. Make sure to send a valid date.\n\n" + DATETIME_EXAMPLES
)
PREDICTION_CREATE_INVALID_CLOSE_DATE_PAST = (
    "Invalid closing date. Make sure to send a date in the future.\n\n" + DATETIME_EXAMPLES
)
PREDICTION_CREATE_REQUEST_CUT_OFF_DATE = (
    "Send the cut off date of the prediction.\nAll bets placed after this time will be removed and"
    " refunded.\nThis action cannot be undone.\nThe time must be after the prediction was opened"
    " and before it was closed or any previously set cut off time\n\n*Opened time*: {}\n*Closed"
    " time*: {}\n*Cut off time*: {}\n\n"
    + DATETIME_EXAMPLES_NO_DURATION
)
PREDICTION_CREATE_INVALID_CUT_OFF_DATE = (
    "Invalid cut off date. Make sure to send a valid date and time after the prediction was opened"
    " and before it was closed or any previously set cut off time.\n\n*Opened time*: {}\n*Closed"
    " time*: {}\n*Cut off time*: {}\n\n"
    + DATETIME_EXAMPLES_NO_DURATION
)
PREDICTION_CUT_OFF_DATE_CONFIRMATION_REQUEST = (
    "Are you sure you want to set the cut off date to *{}*?\n{} bets with a total of ฿{} will be"
    " removed"
)
PREDICTION_SETTING_CANNOT_BE_CHANGED = "This setting cannot be changed"
PREDICTION_CREATE_CLOSE_DATE = (
    PREDICTION_CLOSING_DATE
    + "\n_\\(If set, the prediction will be automatically closed to new bets at this date\\)_"
)
PREDICTION_CREATE_CUT_OFF_DATE = (
    "\n"
    + PREDICTION_CUT_OFF_DATE
    + "\n_\\(If set, all bets placed after this time will be removed and refunded\\)_"
)
PREDICTION_CUT_OFF_DATE_HOW_TO_SET = "\n_You can set it from the edit menu_"
PREDICTION_USER_DISCLAIMER = (
    "\n\n_This prediction was created by a regular user and is not endorsed by the Bounty System"
    " Staff. Make sure to trust the creator before placing a bet._"
)
PREDICTION_DELETE_CONFIRMATION = (
    "Are you sure you want to delete this prediction? This action cannot be undone.\nYou will be"
    " able to create another prediction in *{}*.\n\nIf someone has placed a bet on this"
    " prediction, they will be refunded."
)
PREDICTION_OPEN_CONFIRMATION = (
    "Are you sure you want to open this prediction? You will not be able to change the question or"
    " options after this.\n\nIf the prediction is public, anyone in your groups will be able to"
    " find it.\nYour fellow Crew members will always be able to find it."
)
PREDICTION_CREATE_SUCCESS = "Prediction created successfully"
PREDICTION_DELETE_SUCCESS = "Prediction deleted successfully"
PREDICTION_OPEN_SUCCESS = "Prediction now open for bets"
PREDICTION_ALREADY_OPEN = "Prediction already open for bets"
PREDICTION_ALREADY_CLOSED = "Prediction already closed for bets"
PREDICTION_CLOSE_CONFIRMATION = (
    "Are you sure you want to close this prediction to new bets?\nThis action cannot be undone."
)
PREDICTION_CLOSE_SUCCESS = "Prediction closed successfully"
PREDICTION_INLINE_RESULT_SHARE = "Share Prediction"
PREDICTION_IN_WRONG_STATUS = "Prediction in wrong status"
PREDICTION_SEND_TO_GROUP = (
    "You can send this prediction to groups or topics where you are an Admin and users will be"
    " able to bet on it by replying to the message.\nIf you don't find a group, make sure the Bot"
    f" is a member of the group and use the {CommandName.STATUS.get_formatted()} command in"
    " the group.\nYou can send only once to each group or topic.{}"
)
PREDICTION_SEND_TO_GROUP_NO_GROUPS = "\n\n_No groups found_"
PREDICTION_SEND_TO_GROUP_GROUPS_AVAILABLE = (
    "*\n\nAvailable*:{}\n\nSelect the number of the group \\(no confirmation is required\\)"
)
PREDICTION_SEND_TO_GROUP_GROUPS_ALREADY_SENT = "*\n\nAlready sent*:{}"
PREDICTION_SEND_TO_GROUP_GROUPS_ALREADY_SENT_ITEM = "\n•{}"
PREDICTION_SEND_TO_GROUP_GROUPS_AVAILABLE_ITEM = "\n{}. {}"
PREDICTION_SEND_TO_GROUP_NOT_ADMIN = "You are no longer an Admin"
PREDICTION_SEND_TO_GROUP_ALREADY_SENT = "This prediction has already been sent to this group"
PREDICTION_SET_RESULT = "Select the correct options for this prediction\n\n*{}*\n{}"
PREDICTION_SET_RESULT_CONFIRMATION_REQUEST = (
    "Are you sure you want to set the result of this prediction?\nThe wagers will be distributed"
    " accordingly to the winners and.\nThis action cannot be undone\n\nCorrect options:{}"
)
PREDICTION_SET_RESULT_SUCCESS = "Prediction result set successfully"
PREDICTION_SET_RESULT_CONFIRMATION_REQUEST_NO_CORRECT_OPTION = (
    "No correct option set, wagers will be refunded."
)

# Crew - Private
CREW_SEARCH_ITEM_TEXT = "{} \\(Lv. {}\\)"
CREW_SEARCH_ITEM_TEXT_FILL_IN = "Crew"
CREW_SEARCH_ITEM_LEGEND_CAN_JOIN = "Can join"
CREW_SEARCH_ITEM_LEGEND_CANNOT_JOIN = "Cannot join"
CREW_SEARCH_FILTER_NAME = "Crew name"
CREW_SEARCH_NOT_ALLOWED_TO_VIEW = (
    "Crew information not available.\n\nIf you are the Captain of this Crew, enable `Allow users"
    " to find the Crew from search` option under `Crew->Modify`"
)
CREW_SEARCH_JOIN_NOT_ALLOWED = "The Crew does not allow join requests from search"
CREW_SEARCH_JOIN_CONFIRMATION_REQUEST = (
    "Are you sure you want to send a request to join *{}*?\nYou can request to join a maximum of"
    f" {Env.CREW_JOIN_REQUESTS_PER_COOLDOWN} Crews every"
    f" {Env.CREW_JOIN_REQUEST_COOLDOWN_DURATION} hours and can request to join the same Crew every"
    f" {Env.CREW_JOIN_REQUEST_COOLDOWN_SAME_CREW_DURATION} days."
    "\n\nYour current bounty will be shared with the Crew Captain"
)
CREW_SEARCH_JOIN_SUCCESS = (
    "Request to join *{}* sent successfully, you will be notified when it is accepted"
)
CREW_SEARCH_JOIN_CAPTAIN_REQUEST = (
    "Hi, I'm {} and I would like to join your Crew!\n\nCurrent bounty: ฿{}"
)
CREW_SEARCH_JOIN_CAPTAIN_ACCEPTED = "{} is now a member of your Crew"
CREW_SEARCH_JOIN_CAPTAIN_REJECTED = "You have rejected {}'s request to join your Crew"
CREW_SEARCH_JOIN_CAPTAIN_ERROR = "Error while sending request to Crew Captain"
CREW_SEARCH_JOIN_MAXIMUM_REQUESTS_PER_COOLDOWN = "You can request to join another Crew in {}"
CREW_SEARCH_JOIN_MAXIMUM_REQUESTS_SAME_CREW_PER_COOLDOWN = (
    "You can request to join this Crew again in {}"
)
CREW_USER_NOT_IN_CREW = (
    "You are not in a Crew. Search for one or create your"
    f" own.\n\nCreating a Crew will cost ฿{Env.CREW_CREATE_PRICE.get_belly()}."
)
CREW_NAME_WITH_LEVEL_DEEPLINK = "[{}]({}) \\(Lv. {}\\)"
CREW_OVERVIEW = (
    "*{}* \\(Lv. *{}*\\)"
    "\n\n_{}_"
    "\n\n*Captain*: {}"
    "{}"  # First Mate
    "\n*Formation date*: {} \\({}\\)"
    "\n*Members*: {} \\(Max. {}\\)"
    "{}"  # Active abilities count
    "{}"  # Required bounty
    "{}"  # Treasure chest
    "{}"  # Abilities
    "{}"  # No new members allowed
)
CREW_OVERVIEW_FIRST_MATE = "\n*First Mate*: {}"
CREW_OVERVIEW_ACTIVE_ABILITIES_COUNT = "\n*Active abilities*: {} \\(Max. {}\\)"
CREW_OVERVIEW_TREASURE_CHEST = "\n\n*Treasure Chest*: ฿{}"
CREW_OVERVIEW_ACTIVE_ABILITIES = "\n\n*Abilities*{}"
CREW_OVERVIEW_REQUIRED_BOUNTY = "\n\n*Required bounty*: ฿{}"

CREW_OVERVIEW_NO_NEW_MEMBERS_ALLOWED = (
    "\n\n_No new members allowed until the next weekly leaderboard in {}_"
)
CREW_OVERVIEW_DESCRIPTION_NOT_SET = "No description set"
CREW_MEMBER_ITEM_TEXT = "{}"
CREW_MEMBER_ITEM_ROLE = " \\({}\\)"
# Crew - Member
CREW_MEMBER_ITEM_DETAIL = (
    "*{}*\n\n*Bounty*: ฿{}\n*Join Date*: {} \\({}°\\)\n\nChest contribution: ฿{} \\({}°\\)\nCrew"
    " MVP Bonus: {}{}"
)
CREW_MEMBER_ITEM_DETAIL_ARRESTED = f"\n\n{Emoji.LOG_NEGATIVE}Arrested \\({{}}\\)"
CREW_MEMBER_ITEM_TEXT_FILL_IN = "Crew Member"
CREW_USER_ALREADY_IN_SAME_CREW = "You are already in this Crew"
CREW_USER_ALREADY_IN_CREW = "You are already in a Crew"
CREW_CREATE_USER_NOT_ENOUGH_BOUNTY = (
    f"Insufficient bounty, forming a Crew costs ฿{Env.CREW_CREATE_PRICE.get_belly()}"
)
CREW_CANNOT_CREATE_CREW = "You can create a Crew in {}"
CREW_CREATE_REQUEST_NAME = "Send the name of your Crew"
CREW_CREATE_NAME_ALREADY_EXISTS = "A Crew with this name already exists"
CREW_CREATE_NAME_TOO_LONG = (
    f"Crew name must not exceed {Env.CREW_NAME_MAX_LENGTH.get_int()} characters"
)
CREW_CREATE_SUCCESS = (
    "You are now Captain of the *{}*."
    + f"\n\nHead over to a Chat Group to start recruiting members!"
)
CREW_EDIT_NAME_SUCCESS = "Crew name updated successfully"
CREW_EDIT_REQUEST_DESCRIPTION = (
    f"Send the new description of your Crew \\(max. {Env.CREW_DESCRIPTION_MAX_LENGTH}"
    " characters\\)"
)
CREW_EDIT_DESCRIPTION_TOO_LONG = (
    f"Crew description must not exceed {Env.CREW_DESCRIPTION_MAX_LENGTH.get_int()} characters"
)
CREW_EDIT_DESCRIPTION_SUCCESS = "Crew description updated successfully"
CREW_EDIT_REQUEST_REQUIRED_BOUNTY = "Send the minimum bounty required to join your Crew"
CREW_EDIT_REQUIRED_BOUNTY_SUCCESS = "Required bounty updated successfully"
CREW_MODIFY = (
    "*Name*: {}"
    "\n\n*Description*: {}"
    "\n\n*Required bounty*: ฿{}"
    "\n\nAllow users to find the Crew from search"
    "\n_{}_"
    "\n\nAllow users to request to join the Crew from search"
    "\n_{}_"
    "\n\n What would you like to modify?"
)
CREW_ROLE_CAPTAIN = "Captain"
CREW_ROLE_FIRST_MATE = "First Mate"

# Crew - Join request
CREW_JOIN_REQUEST_CREW_FULL = "The Crew is full"
CREW_NOT_FOUND = "Crew not found"
CREW_JOIN_REQUEST_CAPTION = (
    "My name is {}!!! I do not know who you are, but I ask you!!\nLet me ride on your"
    " ship!!\n\n_Only the [Captain]({}) or [First Mate]({}) can accept or reject this request_"
)
CREW_JOIN_REQUEST_ACCEPTED = "{} is now a member of {}!"
CREW_JOIN_REQUEST_REJECTED = (
    "[Your](tg://user?id={}) request to join the *{}* has been rejected, but don't give up!!"
)
CREW_JOIN_REQUEST_CREW_CANNOT_ACCEPT_USER = "The User cannot join this Crew"
CREW_JOIN_REQUEST_USER_CANNOT_JOIN_CREW = "You cannot join this Crew"
CREW_USER_CANNOT_JOIN_CREW_UNTIL_RESET = (
    "You cannot join a Crew until the next weekly leaderboard in {}"
)
CREW_JOIN_REQUEST_CREW_CANNOT_ACCEPT_NEW_MEMBERS_UNTIL_NEXT_RESET = (
    "The Crew cannot accept new members until the next weekly leaderboard in {}"
)

# Crew - Invite request
CREW_INVITE_REQUEST_CAPTION = (
    "I'm {} and this meeting must be fate, {}! \nWhat do you say to turning the world upside down"
    " with me?"
)
CREW_INVITE_REQUEST_ACCEPTED = "{} is now a member of {}!"
CREW_INVITE_REQUEST_REJECTED = "Invitation to join the *{}* has been rejected by {}"

STEP_REQUIRES_TEXT = "Please send a valid text"
ITEM_NOT_FOUND = "Item not found. If you think this is a mistake, please contact an Admin"
ITEM_NOT_FOUND_NO_CONTACT = "Item not found."
ITEM_IN_WRONG_STATUS = "Item in wrong status"
INLINE_QUERY_ITEM_NOT_FOUND_TITLE = "Item not found"
INLINE_QUERY_ITEM_NOT_FOUND_DESCRIPTION = "Restart the Bot to retrieve a valid url"
INLINE_QUERY_ITEM_NOT_FOUND_MESSAGE = "Error"

# Crew - Leave
CREW_LEAVE_CONFIRMATION = (
    "Are you sure you want to leave the Crew?\nYou will not be able to join another Crew until the"
    " next weekly leaderboard in {}"
)
CREW_LEAVE_CONFIRMATION_LOCATION_DOWNGRADE = (
    " and your location will be downgraded to {} \\(current location: {}\\)"
)
CREW_LEAVE_SUCCESS = "You have left the Crew"

# Crew - Disband
CREW_DISBAND_CONFIRMATION = (
    "Are you sure you want to disband the Crew?\nYou will not be able to create another Crew until"
    " the next bounty reset in {}"
)
CREW_DISBAND_SUCCESS = "You have disbanded the Crew"
CREW_DISBAND_ACTIVE_DAVY_BACK_FIGHT = (
    "The Crew cannot be disbanded during an active Davy Back Fight"
)
CREW_DISBAND_DAVY_BACK_FIGHT_PENALTY = (
    "The Crew cannot be disbanded during a Davy Back Fight penalty period"
)

# Crew - Remove member
CREW_NOT_SAME = "You are not in the same Crew"
CREW_REMOVE_MEMBER_CONFIRMATION = (
    "Are you sure you want to expel {} from the Crew?\nYou will not be able accept new members"
    " until the next weekly leaderboard in {}"
)
CREW_REMOVE_MEMBER_SUCCESS = "{} has been expelled from the Crew"
CREW_REMOVE_MEMBER_ACTIVE_DAVY_BACK_FIGHT = (
    "Members cannot be removed or leave the Crew during an active Davy Back Fight"
)
CREW_REMOVE_MEMBER_DAVY_BACK_FIGHT_PENALTY = (
    "Members cannot be removed or leave the Crew during a Davy Back Fight penalty period"
)

# Crew - Promote to First Mate
CREW_PROMOTE_TO_FIRST_MATE_CREW_ALREADY_HAS_FIRST_MATE = "The Crew already has a First Mate"
CREW_PROMOTE_TO_FIRST_MATE_CANNOT_PROMOTE_UNTIL_NEXT_LEADERBOARD = (
    "You cannot promote a member to First Mate until the next weekly leaderboard in {}"
)
CREW_FIRST_MATE_PRIVILEGES = "\n• Accept new members \n• Activate Crew Abilities"
CREW_PROMOTE_TO_FIRST_MATE_CONFIRMATION = (
    "Are you sure you want to promote {} to First Mate?\nThey will gain the following privileges:"
    + CREW_FIRST_MATE_PRIVILEGES
)
CREW_PROMOTE_TO_FIRST_MATE_SUCCESS = "{} has been promoted to First Mate"

# Crew - Demote from First Mate
CREW_DEMOTE_FROM_FIRST_MATE_IS_NOT_FIRST_MATE = "{} is not a First Mate"
CREW_DEMOTE_FROM_FIRST_MATE_CONFIRMATION = (
    "Are you sure you want to demote {} from First Mate?\nYou will not be able to promote another"
    " member to First Mate until the next weekly leaderboard in {}"
)
CREW_DEMOTE_FROM_FIRST_MATE_SUCCESS = "{} has been demoted from First Mate"
CREW_POST_BAIL_MEMBER_NOT_ARRESTED_TEMPORARY = "The member does not have a temporary sentence"
CREW_POST_BAIL_NOT_ENOUGH_BOUNTY = "You need ฿{} to post bail.\n\nCurrent bounty: ฿{}"
CREW_POST_BAIL_CANNOT_POST_BAIL_FOR_SELF = "You cannot post bail for yourself"
CREW_POST_BAIL_CONFIRMATION_REQUEST = (
    "Are you sure you want to post bail for {}?"
    "\nFor each remaining minute in the sentence, "
    f"you will be charged *฿{Env.IMPEL_DOWN_BAIL_PER_MINUTE.get_belly()}*"
    "\n\nTotal bail: *฿{}*"
)
CREW_POST_BAIL_SUCCESS = "Bail posted successfully"
# Crew abilities
CREW_ABILITIES = (
    "*Crew Abilities*\n\nAbilities mimic the effects of Devil Fruits and are extended to all"
    " members of the Crew."
    + "\nEach ability cost depends on the current Crew level and lasts for"
    f" {Env.CREW_ABILITY_DURATION_DAYS.get_int()} days."
    + "\n{}\n\nNext ability cost: ฿*{}*\nCrew chest: ฿{}"
)
CREW_ABILITY_NO_ABILITIES = "\n_No abilities are currently activated in this Crew_"
CREW_ABILITY_ITEM_TEXT = "\n• {}{} \\({}%\\)"
CREW_ABILITY_ITEM_TEXT_DURATION = "\nRemaining time: {}"
CREW_POWERUP_INSUFFICIENT_CREW_CHEST = (
    "Insufficient Crew Chest\n\nCrew chest: ฿{}\nPower-up cost: ฿{}"
)
CREW_ABILITY_MAX_ABILITIES_REACHED = "Max number of active abilities reached"
CREW_ABILITY_ACTIVATE_CHOOSE = (
    "Choose an ability you want to use, or go with Random' for a surprise. "
    "\n\nIf you pick a specific ability, it will always be set at "
    f"{Env.CREW_ABILITY_DEFAULT_VALUE_PERCENTAGE.get_int()}%."
    "\n\nIf you choose Random instead you'll get a completely random ability and its "
    "value can be anywhere between "
    f"{Env.CREW_ABILITY_RANDOM_MIN_VALUE_PERCENTAGE.get_int()}% "
    f"and {Env.CREW_ABILITY_RANDOM_MAX_VALUE_PERCENTAGE.get_int()}%."
)
CREW_ABILITY_ACTIVATE_CHOOSE_RECAP = (
    "\n\n*Ability*: {}\n*Value*: {}\n*Duration*: {} days\n*Cost*: ฿{}"
)
CREW_ABILITY_ACTIVATE_CHOOSE_CONFIRMATION_REQUEST = (
    "Are you sure you want to activate the following ability?" + CREW_ABILITY_ACTIVATE_CHOOSE_RECAP
)
CREW_ABILITY_ACTIVATE_SUCCESS = (
    "Ability activated successfully" + CREW_ABILITY_ACTIVATE_CHOOSE_RECAP
)

# Crew power-up
CREW_POWERUP = (
    "*Level*"
    "\nBy leveling-up a, the Crew can increase the number of allowed abilities or members slot"
    " and reduce income tax for the members."
    "\n\n_*Current level:*_ {}"
    "\n\n\n*Abilities*"
    "\nAbilities mimic the effects of Devil Fruits and are extended to all members of the Crew."
    "\n\n_*Current abilities:*_"
    "{}"
    "\n\nOnly the Crew Captain or First Mate can enable a power-up"
)

# Crew level
CREW_LEVEL_UP_RECAP = "*Upgrade*: +1 {} slot \\({}->{}\\)\n*Income Tax*: -1 Bracket\n*Cost*: ฿{}"
CREW_LEVEL = (
    "*Level*"
    "\n\nBy leveling-up a, the Crew can increase the number of allowed abilities or members slot"
    " and reduce income tax for the members."
    "\nEach level doubles the price of the next one."
    "\n\n*Current level*: {}"
    "\n*Max members*: {}"
    "\n*Max abilities*: {}"
    "\n\n*Next level*: {}"
    "\n{}"
    "\nCrew chest: ฿{}"
)
CREW_LEVEL_UPGRADE_TYPE_MEMBER = "member"
CREW_LEVEL_UPGRADE_TYPE_ABILITY = "ability"

CREW_LEVEL_UP_CONFIRMATION_REQUEST = "Are you sure you want to level up the Crew?\n\n{}"
CREW_LEVEL_UP_SUCCESS = "Crew leveled up successfully\n\n{}"
CREW_DAVY_BACK_FIGHT_ITEM_TEXT = "{} vs. {}"
CREW_DAVY_BACK_FIGHT_ITEM_TEXT_FILL_IN = "Davy Back Fight"
CREW_DAVY_BACK_FIGHT_ITEM_DETAIL_TEXT = (
    "*{}*: {}\n\n*Start date*: {}\n*End date*: {}\n*Players*: {}{}\n\n{}{}"
)
CREW_DAVY_BACK_FIGHT_ITEM_DETAIL_CONTRIBUTIONS = (
    "\n\n*Total gained*: ฿{}\n*Opponent total gained*: ฿{}\n*Top Crew Player*: {}\\(฿{}\\)"
)
CREW_DAVY_BACK_FIGHT_ITEM_DETAIL_END = "\n\nPenalty end: {}{}{}"
CREW_DAVY_BACK_FIGHT_ITEM_DETAIL_CONSCRIPTED_MEMBER = "\nConscripted member: {}"

CREW_DAVY_BACK_FIGHT_REQUEST_ERROR_SAME_CREW = "Cannot challenge your own Crew"
CREW_DAVY_BACK_FIGHT_REQUEST_ERROR_ALREADY_IN_FIGHT = "Crew already in a Davy Back Fight"
CREW_DAVY_BACK_FIGHT_REQUEST_ERROR_ALREADY_PENDING = (
    "Crew already has a pending Davy Back Fight request"
)
CREW_DAVY_BACK_FIGHT_REQUEST_ERROR_IN_PENALTY_PERIOD = (
    "Crew is in a penalty period and cannot participate in a Davy Back Fight"
)
CREW_DAVY_BACK_FIGHT_REQUEST_ERROR_TOO_LATE = (
    "Davy Back Fight cannot be initiated less than {} hours before bounty reset"
)
CREW_DAVY_BACK_FIGHT_REQUEST_ERROR_MINIMUM_PARTICIPANTS = (
    "Crew must have at least {} members to participate in a Davy Back Fight"
)
# TODO add info about dbf
CREW_DAVY_BACK_FIGHT_REQUEST_NUMBER_OF_PARTICIPANTS = (
    "How many members from each Crew will participate in the Davy Back Fight?"
)
CREW_DAVY_BACK_FIGHT_REQUEST_CONFIRMATION = (
    "Are you sure you want to challenge *{}* to a Davy Back Fight with {} members from each Crew?"
    "\n\nThey will have {} to accept or reject"
)
CREW_DAVY_BACK_FIGHT_REQUEST_SUCCESS = (
    "Davy Back Fight challenge to *{}* sent successfully, you will be notified when it is accepted"
)
CREW_DAVY_BACK_FIGHT_CAPTAIN_REQUEST = (
    "New Davy Back Fight challenge from {}!"
    "\n\n*Number of participants*: {}"
    "\n\nYou have {} to accept the challenge"
)
CREW_DAVY_BACK_FIGHT_CAPTAIN_ACCEPTED = (
    "Davy Back Fight against {} accepted, it will start in"
    f" {Env.CREW_DAVY_BACK_FIGHT_START_WAIT_TIME.get()} minutes.\n\nClick `{KEY_MANAGE}` to review"
    " and change the players"
)
CREW_DAVY_BACK_FIGHT_CAPTAIN_REJECTED = "Davy Back Fight against {} rejected"
CREW_DAVY_BACK_FIGHT_USER_NOT_MEMBER_OF_PARTICIPATING_CREW = (
    "User not a member of a participating Crew"
)
CREW_DAVY_BACK_FIGHT_USER_ALREADY_PARTICIPANT = "User already a participant"
CREW_DAVY_BACK_FIGHT_NOT_ENOUGH_MEMBERS = (
    "Not enough members to participate in the Davy Back Fight"
)
CREW_DAVY_BACK_FIGHT_PARTICIPANTS_SELECT_ERROR_ALREADY_STARTED = (
    "The Davy Back Fight has already started"
)
CREW_DAVY_BACK_FIGHT_PARTICIPANTS_SELECT_ERROR_NOT_ENOUGH_MEMBERS = "No extra member to swap with"
CREW_DAVY_BACK_FIGHT_PARTICIPANTS_SELECT = (
    "Choose the members you want to participate in the Davy Back Fight.\n\nRemaining time: {}"
)
CREW_DAVY_BACK_FIGHT_PARTICIPANTS_SELECT_SWAP = "Select the member you want to swap with"
CREW_DAVY_BACK_FIGHT_PARTICIPANTS_SELECT_SWAP_SUCCESS = "Participant swapped successfully"
CREW_DAVY_BACK_FIGHT_PARTICIPANTS = "*Team Mates*{}\n\n*Opponents*{}"
CREW_DAVY_BACK_FIGHT_PARTICIPANTS_ITEM = "\n{} - ฿{}"

# Bounty Gift
BOUNTY_GIFT_NO_AMOUNT = (
    "You need to specify the amount of belly you want to gift\n\nExample:"
    f" {CommandName.BOUNTY_GIFT.get_formatted()} 10.000.000"
)
BOUNTY_GIFT_REQUEST = (
    "Are you sure you want to gift ฿*{}* to {}?\n\nTax: ฿{} \\({}%\\)\nTotal: ฿*{}*"
)
BOUNTY_GIFT_CONFIRMED = "You have gifted ฿*{}* to {}\n\nTax: ฿{} \\({}%\\)\nTotal: ฿*{}*"
BOUNTY_GIFT_CANCELLED = "Gift cancelled"
BOUNTY_GIFT_NOT_ENOUGH_BOUNTY = (
    "You do not have enough belly to gift\n\nAvailable belly: ฿{}\nGift amount: ฿*{}*\nTax: ฿{}"
    " \\({}%\\)\nTotal: ฿*{}*\n\nYou can gift up to ฿`{}`"
)

# Bounty Loan
BOUNTY_LOAN_INVALID_COMMAND = (
    "You need to specify the amount to loan, the amount to repay and the duration\n\nExample:"
    f" {CommandName.BOUNTY_LOAN.get_formatted()} 100mil 150mil 1day"
)
BOUNTY_LOAN_LOANER = "\nLoaner: {}"
BOUNTY_LOAN_BORROWER = "\nBorrower: {}"
BOUNTY_LOAN_AMOUNT = "\nAmount: ฿*{}*"
BOUNTY_LOAN_REPAY_AMOUNT = "\nRepay amount: ฿*{}*"
BOUNTY_LOAN_AMOUNT_REPAID = "\nAmount paid: ฿*{}*"
BOUNTY_LOAN_AMOUNT_REMAINING = "\nAmount remaining: ฿*{}*"
BOUNTY_LOAN_AMOUNT_REMAINING_MONOSPACE = "\nAmount remaining: ฿`{}`"
BOUNTY_LOAN_DATE = "\nDate: *{}*"
BOUNTY_LOAN_DURATION = "\nDuration: *{}*"
BOUNTY_LOAN_DEADLINE_DATE = "\nDeadline: *{}*"
BOUNTY_LOAN_TAX = "\nTax: ฿{} \\({}%\\)"
BOUNTY_LOAN_TOTAL = "\nTotal: ฿*{}*"
BOUNTY_LOAN_STATUS = "\n\nStatus: {}*{}*"
BOUNTY_LOAN_CANCELLED = "Loan cancelled"
BOUNTY_LOAN_NOT_ENOUGH_BOUNTY = (
    "You do not have enough belly to loan\n\nAvailable belly: ฿{}\nLoan amount: ฿*{}*\nTax: ฿{}"
    " \\({}%\\)\nTotal: ฿*{}*\n\nYou can loan up to ฿`{}`"
)
BOUNTY_LOAN_ISSUE_COOLDOWN_ACTIVE = "You can issue a loan in *{}*"
BOUNTY_LOAN_MAX_DURATION_EXCEEDED = (
    f"A loan cannot last more than {Env.BOUNTY_LOAN_MAX_DURATION_DAYS.get_int()} days"
)
BOUNTY_LOAN_STATUS_AWAITING_LOANER_CONFIRMATION = "Awaiting loaner confirmation"
BOUNTY_LOAN_STATUS_AWAITING_BORROWER_CONFIRMATION = "Awaiting borrower confirmation"
BOUNTY_LOAN_STATUS_ACTIVE = "Active"
BOUNTY_LOAN_STATUS_REPAID = "Re-paid"
BOUNTY_LOAN_STATUS_EXPIRED = "Expired"
BOUNTY_LOAN_STATUS_FORGIVEN = "Forgiven"
BOUNTY_LOAN_EXPIRED_ACTION_WARNING_PREFIX = "\n\n_In case the loan is not repaid in time, "
BOUNTY_LOAN_EXPIRED_ACTION_SUFFIX = (
    "\nThe loan will be automatically forgiven if"
    f" {Env.BOUNTY_LOAN_FORGIVENESS_DAYS.get_int()} days have passed since the expiration date and"
    " at least double the loan amount has been repaid."
)
BOUNTY_LOAN_EXPIRED_ACTION_PREFIX = "\n\n_Since the loan was not repaid in time, "
BOUNTY_LOAN_EXPIRED_ACTION_LOANER = (
    "{}% of all new gained bounty by {} will be transferred to you until the loan is repaid."
    + BOUNTY_LOAN_EXPIRED_ACTION_SUFFIX
    + "_"
)
BOUNTY_LOAN_EXPIRED_ACTION_BORROWER = (
    "{}% of all new gained bounty will be transferred to {} until the loan is repaid."
    + BOUNTY_LOAN_EXPIRED_ACTION_SUFFIX
    + "_"
)
BOUNTY_LOAN_EXPIRED_ACTION_LOANER_AND_BORROWER = (
    "{}% of all new gained bounty by {} will be transferred to {} until the loan is repaid."
    + BOUNTY_LOAN_EXPIRED_ACTION_SUFFIX
    + "_"
)
BOUNTY_LOAN_REQUEST = (
    "*New Loan*\n"
    + BOUNTY_LOAN_LOANER
    + BOUNTY_LOAN_BORROWER
    + BOUNTY_LOAN_AMOUNT
    + BOUNTY_LOAN_REPAY_AMOUNT
    + BOUNTY_LOAN_DURATION
    + BOUNTY_LOAN_TAX
    + BOUNTY_LOAN_TOTAL
    + BOUNTY_LOAN_STATUS
    + BOUNTY_LOAN_EXPIRED_ACTION_WARNING_PREFIX
    + BOUNTY_LOAN_EXPIRED_ACTION_LOANER_AND_BORROWER
)
BOUNTY_LOAN_REQUEST_PREDATORY_WARNING = (
    f"\n\n{Emoji.WARNING_STRONG}Warning, this is a predatory loan with a *{{}}%* interest rate."
)
BOUNTY_LOAN_REQUEST_MANAGE_TEXT = "\n\n" + surround_with_arrows("[Manage Loan]({})")

# Bounty loan - Private Chat
BOUNTY_LOAN_ITEM_TEXT = "{} ฿{} {} {}"
BOUNTY_LOAN_ITEM_TEXT_FILL_IN = "Loan"
BOUNTY_LOAN_ITEM_NOT_ACTIVE = "This loan is no longer active"
BOUNTY_LOAN_ITEM_PAY_REQUEST = (
    BOUNTY_LOAN_REPAY_AMOUNT.strip()
    + BOUNTY_LOAN_AMOUNT_REPAID
    + BOUNTY_LOAN_AMOUNT_REMAINING_MONOSPACE
    + "\nCurrent bounty: ฿`{}`"
    + "\n\n_Please send the amount you want to pay \\(send \\* to repay the maximum allowed by"
    " your bounty\\)_"
)
BOUNTY_LOAN_ITEM_PAY_CONFIRMATION_REQUEST = "Are you sure you want to pay ฿*{}* for this loan?"
BOUNTY_LOAN_ITEM_PAY_SUCCESS = "You have successfully paid ฿{} for this loan"
BOUNTY_LOAN_ITEM_FORGIVE_CONFIRMATION_REQUEST = (
    BOUNTY_LOAN_REPAY_AMOUNT.strip()
    + BOUNTY_LOAN_AMOUNT_REPAID
    + BOUNTY_LOAN_AMOUNT_REMAINING_MONOSPACE
    + "\n\nAre you sure you want to forgive this loan?\nYou will not be able to collect the"
    " remaining amount"
)
BOUNTY_LOAN_ITEM_FORGIVE_SUCCESS = "You have forgiven this loan"
BOUNTY_LOAN_SOURCE = "\nSource: [{}]({})"
BOUNTY_LOAN_SOURCE_USER = "Loan"
BOUNTY_LOAN_SOURCE_PLUNDER = "Plunder"
BOUNTY_LOAN_SOURCE_IMPEL_DOWN_BAIL = "Impel Down Bail"

# Notification - Categories
NOTIFICATION_CATEGORY_BOUNTY_GIFT = "Bounty Gift"
NOTIFICATION_CATEGORY_BOUNTY_LOAN = "Bounty Loan"
NOTIFICATION_CATEGORY_CREW = "Crew"
NOTIFICATION_CATEGORY_DELETED_MESSAGE = "Deleted Message"
NOTIFICATION_CATEGORY_GAME = "Game"
NOTIFICATION_CATEGORY_IMPEL_DOWN = "Impel Down"
NOTIFICATION_CATEGORY_LOCATION = "Location"
NOTIFICATION_CATEGORY_PREDICTION = "Prediction"
NOTIFICATION_CATEGORY_DEVIL_FRUIT = "Devil Fruit"
NOTIFICATION_CATEGORY_WARLORD = "Warlord"
NOTIFICATION_CATEGORY_DAVY_BACK_FIGHT = "Davy Back Fight"

# Notification - Crew Leave
CREW_LEAVE_NOTIFICATION = "{} has left the Crew"
CREW_LEAVE_NOTIFICATION_DESCRIPTION = (
    "If to be notified when a member leaves the Crew. \nApplicable only if you are the Captain or"
    " First Mate of the Crew."
)
CREW_LEAVE_NOTIFICATION_KEY = "Crew leave"
# Notification - Crew Member removed
CREW_MEMBER_REMOVE_NOTIFICATION = "You have been expelled from the Crew"
CREW_MEMBER_REMOVE_NOTIFICATION_DESCRIPTION = (
    "If to be notified when you are expelled from the Crew."
)
CREW_MEMBER_REMOVE_NOTIFICATION_KEY = "Crew member expelled"
# Notification - Crew Disband
CREW_DISBAND_NOTIFICATION = "Your Crew has been disbanded"
CREW_DISBAND_NOTIFICATION_DESCRIPTION = "If to be notified when your Crew is disbanded."
CREW_DISBAND_NOTIFICATION_KEY = "Crew disband"
# Notification - Crew disband warning
CREW_DISBAND_WARNING_NOTIFICATION = (
    "You have not been active in the current Bounty season."
    "\nIn case of continued inactivity, your Crew will be disbanded on the next bounty reset in {}"
)
CREW_DISBAND_WARNING_NOTIFICATION_DESCRIPTION = (
    "If to be notified a week before your Crew is disbanded due to inactivity."
    "\nApplicable only if you are the Captain of the Crew."
)
CREW_DISBAND_WARNING_NOTIFICATION_KEY = "Crew disband warning"
# Notification - Crew ability activated
CREW_ABILITY_ACTIVATED_NOTIFICATION = (
    "The following ability has been activated in your Crew:\n\n*Ability*: {}"
    " \\({}%\\)\n*Duration*: {}"
)
CREW_ABILITY_ACTIVATED_NOTIFICATION_DESCRIPTION = (
    "If to be notified when an ability is activated in your Crew."
)
CREW_ABILITY_ACTIVATED_NOTIFICATION_KEY = "Crew ability activated"
# Notification - Crew first mate promotion
CREW_FIRST_MATE_PROMOTION_NOTIFICATION = (
    "Congratulations! You have been promoted to First Mate of the Crew.\n\nPrivileges:"
    + CREW_FIRST_MATE_PRIVILEGES
)
CREW_FIRST_MATE_PROMOTION_NOTIFICATION_DESCRIPTION = (
    "If to be notified when you are promoted to First Mate of the Crew."
)
CREW_FIRST_MATE_PROMOTION_NOTIFICATION_KEY = "First Mate promotion"
# Notification - Crew first mate demotion
CREW_FIRST_MATE_DEMOTION_NOTIFICATION = "You have been demoted from First Mate of the Crew."
CREW_FIRST_MATE_DEMOTION_NOTIFICATION_DESCRIPTION = (
    "If to be notified when you are demoted from First Mate of the Crew."
)
CREW_FIRST_MATE_DEMOTION_NOTIFICATION_KEY = "First Mate demotion"
# Notification - Crew join request accepted
CREW_JOIN_REQUEST_ACCEPTED_NOTIFICATION = (
    "Congratulations! Your request to join *{}* has been accepted"
)
CREW_JOIN_REQUEST_ACCEPTED_NOTIFICATION_DESCRIPTION = (
    "If to be notified when your request to join a Crew is accepted."
)
CREW_JOIN_REQUEST_ACCEPTED_NOTIFICATION_KEY = "Join request accepted"
# Notification - Crew join request rejected
CREW_JOIN_REQUEST_REJECTED_NOTIFICATION = "Your request to join *{}* has been rejected"
CREW_JOIN_REQUEST_REJECTED_NOTIFICATION_DESCRIPTION = (
    "If to be notified when your request to join a Crew is rejected."
)
CREW_JOIN_REQUEST_REJECTED_NOTIFICATION_KEY = "Join request rejected"
# Notification - Davy Back Fight request accepted
DAVY_BACK_FIGHT_REQUEST_ACCEPTED_NOTIFICATION = (
    "{} has accepted your Crew's Davy Back Fight challenge, it will start in"
    f" {Env.CREW_DAVY_BACK_FIGHT_START_WAIT_TIME.get()} minutes.\n\nClick `{KEY_MANAGE}` to review"
    " and change the players"
)
DAVY_BACK_FIGHT_REQUEST_ACCEPTED_NOTIFICATION_DESCRIPTION = (
    "If to be notified when your Crew's Davy Back Fight challenge is accepted."
    "\nApplicable only if you are the Captain of the Crew"
)
DAVY_BACK_FIGHT_REQUEST_ACCEPTED_NOTIFICATION_KEY = "Challenge accepted"
# Notification - Davy Back Fight request rejected
CREW_DAVY_BACK_FIGHT_REQUEST_REJECTED_NOTIFICATION = (
    "{} has rejected your Crew's Davy Back Fight challenge"
)
DAVY_BACK_FIGHT_REQUEST_REJECTED_NOTIFICATION_DESCRIPTION = (
    "If to be notified when your Crew's Davy Back Fight challenge is rejected."
    "\nApplicable only if you are the Captain of the Crew"
)
DAVY_BACK_FIGHT_REQUEST_REJECTED_NOTIFICATION_KEY = "Challenge rejected"
# Notification - Davy Back Fight start
DAVY_BACK_FIGHT_START_NOTIFICATION = (  # TODO add rules
    "You have been chosen as a Player for a Davy Back Fight against {}"
)
DAVY_BACK_FIGHT_START_NOTIFICATION_DESCRIPTION = (
    "If to be notified when a Davy Back Fight in which you are a Player starts"
)
DAVY_BACK_FIGHT_START_NOTIFICATION_KEY = "Start"

# Notification - Game turn
GAME_TURN_NOTIFICATION = (
    f"It's your turn to play in {{}} against {{}}.\n\n[{Emoji.RIGHT_ARROW}Click here to view the"
    f" game{Emoji.LEFT_ARROW}]"
    + "({})"
)
GAME_TURN_NOTIFICATION_DESCRIPTION = (
    "If to be notified when it is your turn to play in a game if no action is taken for"
    f" {Env.GAME_TURN_NOTIFICATION_TIME.get_int()} seconds"
)
GAME_TURN_NOTIFICATION_KEY = "Game turn"
# Notification - Location
LOCATION_UPDATE_NOTIFICATION = "{}Congratulations {}!\nYou are now {} {}\n\n{}"
LOCATION_NEXT_LEVEL_REQUIREMENT = "_Requirement for next location: ฿*{}*_"
LOCATION_CURRENT_LEVEL_MAX = "_You have reached the maximum location_"
LOCATION_UPDATE_NOTIFICATION_DESCRIPTION = "If to be notified when you level up to a new location."
LOCATION_UPDATE_NOTIFICATION_KEY = "Location update"
# Notification - Impel Down restriction placed
IMPEL_DOWN_RESTRICTION_PLACED_NOTIFICATION = (
    f"{Emoji.DISCIPLINARY_ACTION}*DISCIPLINARY ACTION*{Emoji.DISCIPLINARY_ACTION}\n\n*Reason*:"
    " {}\n\n*Restrictions*:{}{}{}"
)
IMPEL_DOWN_RESTRICTION_PLACED_NOTIFICATION_BOUNTY_HALVED = "\n- Bounty halved"
IMPEL_DOWN_RESTRICTION_PLACED_NOTIFICATION_BOUNTY_ERASED = "\n- Bounty erased"
IMPEL_DOWN_RESTRICTION_PLACED_NOTIFICATION_WITH_DURATION = (
    "\n- You can't acquire any new bounty\n- You can't appear in the leaderboard\n- You can't"
    " challenge other users or play games\n- You can't bet in polls"
)
IMPEL_DOWN_RESTRICTION_PLACED_NOTIFICATION_DURATION = "\n\n*Duration*: {}"
IMPEL_DOWN_RESTRICTION_PLACED_NOTIFICATION_DURATION_PERMANENT = "Permanent"
IMPEL_DOWN_RESTRICTION_PLACED_NOTIFICATION_DURATION_BAIL = (
    "\n\nA Crew member can post bail for you, at a cost of"
    f" ฿*{Env.IMPEL_DOWN_BAIL_PER_MINUTE.get_belly()}* for every minute left in your sentence"
    f" \n\\(`{PVT_KEY_CREW}`->`{PVT_KEY_CREW_MEMBERS}`->"
    f"Select->`{PVT_KEY_CREW_MEMBER_POST_BAIL}`\\)"
)
IMPEL_DOWN_RESTRICTION_PLACED_NOTIFICATION_DESCRIPTION = (
    "If to be notified when you are restricted"
)
IMPEL_DOWN_RESTRICTION_PLACED_NOTIFICATION_KEY = "Restriction placed"
# Notification - Impel Down restriction removed
IMPEL_DOWN_RESTRICTION_REMOVED_NOTIFICATION = "All restrictions have been removed"
IMPEL_DOWN_RESTRICTION_REMOVED_NOTIFICATION_DESCRIPTION = (
    "If to be notified when all restrictions are removed"
)
IMPEL_DOWN_RESTRICTION_REMOVED_NOTIFICATION_KEY = "Restriction removed"
# Notification - Impel Down bail posted
IMPEL_DOWN_BAIL_POSTED_NOTIFICATION = (
    "{} has paid *฿{}* to free you from Impel Down \\({} was left in your sentence\\)"
)
IMPEL_DOWN_BAIL_POSTED_NOTIFICATION_DESCRIPTION = "If to be notified when bail is posted"
IMPEL_DOWN_BAIL_POSTED_NOTIFICATION_KEY = "Bail posted"

# Notification - Prediction result
PREDICTION_RESULT_NOTIFICATION = 'You *{}* ฿{} in the prediction "*{}*"{}{}{}'
PREDICTION_RESULT_NOTIFICATION_WAGER_REFUNDED = "_\n\n\\(Your wager was refunded\\)_"
PREDICTION_RESULT_NOTIFICATION_WAGER_REFUNDED_PARTIAL = "_\n\n\\(You have been refunded ฿{}\\)_"
PREDICTION_RESULT_NOTIFICATION_WAGER_REFUNDED_NO_CORRECT_OPTIONS = (
    "_\n\n\\(Your wager was refunded because there were no correct options\\)_"
)
PREDICTION_RESULT_NOTIFICATION_OPTION = "\n{}{}"
PREDICTION_RESULT_NOTIFICATION_OPTION_NO_EMOJI = "\n- {}"
PREDICTION_RESULT_NOTIFICATION_YOUR_OPTION = "\n\n*Your option*: {}"
PREDICTION_RESULT_NOTIFICATION_YOUR_OPTIONS = "\n\n*Your options*: {}"
PREDICTION_RESULT_NOTIFICATION_CORRECT_OPTION = "\n\n*Correct option*: {}"
PREDICTION_RESULT_NOTIFICATION_CORRECT_OPTIONS = "\n\n*Correct options*: {}"
PREDICTION_RESULT_NOTIFICATION_DESCRIPTION = (
    "If to be notified of the outcome of a prediction you participated in"
)
PREDICTION_RESULT_NOTIFICATION_KEY = "Prediction result"
# Notification - Prediction bet invalid
PREDICTION_BET_INVALID_BET_HAS = "bet has"
PREDICTION_BET_INVALID_BETS_HAVE = "bets have"
PREDICTION_BET_INVALID_NOTIFICATION = (
    'The following {} been removed from the prediction "*{}*"'
    + " because {} placed after the cut off time \\({}\\):\n{}"
    + "\n\n_You have been refunded ฿{}_"
)
PREDICTION_BET_INVALID_NOTIFICATION_OPTION = "\n- {} \\({}\\)"
PREDICTION_BET_INVALID_NOTIFICATION_DESCRIPTION = (
    "If to be notified when a bet you placed is removed from a because it was placed after the cut"
    " off time"
)
PREDICTION_BET_INVALID_NOTIFICATION_KEY = "Prediction bet removed"
# Notification - Deleted message because of arrest
ABOVE_MESSAGE_DELETED_FROM_CHAT_GROUP = (
    f"The above message was deleted from the Group Chat because you "
)
DELETED_MESSAGE_ARREST_NOTIFICATION = f"{ABOVE_MESSAGE_DELETED_FROM_CHAT_GROUP} are arrested"
DELETED_MESSAGE_ARREST_NOTIFICATION_DESCRIPTION = (
    "If to be notified when a message you sent in the Group Chat was deleted because you are"
    " arrested"
)
DELETED_MESSAGE_ARREST_NOTIFICATION_KEY = "Deleted message arrest"
# Notification - Deleted message because of user is muted
DELETED_MESSAGE_MUTE_NOTIFICATION = f"{ABOVE_MESSAGE_DELETED_FROM_CHAT_GROUP} are muted"
DELETED_MESSAGE_MUTE_NOTIFICATION_DESCRIPTION = (
    "If to be notified when a message you sent in the Group Chat was deleted because you are muted"
)
DELETED_MESSAGE_MUTE_NOTIFICATION_KEY = "Deleted message mute"
# Notification - Deleted message because of user has not reached the required location
DELETED_MESSAGE_LOCATION_NOTIFICATION = (
    f"{ABOVE_MESSAGE_DELETED_FROM_CHAT_GROUP} have not reached the required location to send this"
    " type of message.\n\n*Your location*: {}\n*Required location*: {}"
)
DELETED_MESSAGE_LOCATION_NOTIFICATION_DESCRIPTION = (
    "If to be notified when a message you sent in the Group Chat was deleted because you have not"
    " reached the required location to send that type of message"
)
DELETED_MESSAGE_LOCATION_NOTIFICATION_KEY = "Deleted message location"
# Notification - Bounty Gift
BOUNTY_GIFT_RECEIVED_NOTIFICATION = "You have been gifted ฿{} by {}"
BOUNTY_GIFT_RECEIVED_NOTIFICATION_DESCRIPTION = "If to be notified when you are gifted bounties"
BOUNTY_GIFT_RECEIVED_NOTIFICATION_KEY = "Bounty gift"
# Notification - Devil Fruit Awarded
DEVIL_FRUIT_EAT_OR_SELL = (
    "\n\nYou can eat it or sell it with the"
    f" {CommandName.DEVIL_FRUIT_SELL.get_formatted()} command in a group"
)
DEVIL_FRUIT_AWARDED_NOTIFICATION = (
    "You have been awarded the following Devil Fruit:\n\n*{}*\nReason: {}"
    + DEVIL_FRUIT_EAT_OR_SELL
)
DEVIL_FRUIT_AWARDED_NOTIFICATION_DESCRIPTION = (
    "If to be notified when you are awarded a Devil Fruit"
)
DEVIL_FRUIT_AWARDED_NOTIFICATION_KEY = "Devil Fruit award"
# Notification - Devil Fruit Expired
DEVIL_FRUIT_EXPIRED_NOTIFICATION = "Your Devil Fruit *{}* has expired and has been revoked"
DEVIL_FRUIT_EXPIRED_NOTIFICATION_DESCRIPTION = "If to be notified when your Devil Fruit expires"
DEVIL_FRUIT_EXPIRED_NOTIFICATION_KEY = "Devil Fruit expired"
# Notification - Devil Fruit revoke
DEVIL_FRUIT_REVOKE_NOTIFICATION = "Your Devil Fruit *{}* has been revoked"
DEVIL_FRUIT_REVOKE_NOTIFICATION_DESCRIPTION = "If to be notified when your Devil Fruit is revoked"
DEVIL_FRUIT_REVOKE_NOTIFICATION_KEY = "Devil Fruit revoked"
# Notification - Devil Fruit revoke warning
DEVIL_FRUIT_REVOKE_WARNING_NOTIFICATION = (
    "You have not appeared in the last"
    f" {Env.DEVIL_FRUIT_MAINTAIN_MIN_LATEST_LEADERBOARD_APPEARANCE.get_int() - 1} leaderboards."
    "\nIf you do not appear in the next leaderboard, your Devil Fruit *{}* will be revoked."
)
DEVIL_FRUIT_REVOKE_WARNING_NOTIFICATION_DESCRIPTION = (
    "If to be notified a week before the Devil Fruit you ate is revoked due to not appearing in"
    " the leaderboard for"
    f" {Env.DEVIL_FRUIT_MAINTAIN_MIN_LATEST_LEADERBOARD_APPEARANCE.get()} consecutive leaderboards"
)
DEVIL_FRUIT_REVOKE_WARNING_NOTIFICATION_KEY = "Devil Fruit revoke warning"
# Notification - Bounty Loan
BOUNTY_LOAN_NOTIFICATION_GO_TO_ITEM_BUTTON_TEXT = "Go to loan"
# Notification - Bounty Loan Payment
BOUNTY_LOAN_PAYMENT_NOTIFICATION = "You have received a payment of ฿{} from {} for your loan"
BOUNTY_LOAN_PAYMENT_NOTIFICATION_DESCRIPTION = (
    "If to be notified when you receive a payment for your loan"
)
BOUNTY_LOAN_PAYMENT_NOTIFICATION_KEY = "Bounty loan payment"
# Notification - Bounty Loan Forgiven
BOUNTY_LOAN_FORGIVEN_NOTIFICATION = "Your loan of ฿{} from {} has been forgiven"
BOUNTY_LOAN_FORGIVEN_NOTIFICATION_DESCRIPTION = "If to be notified when your loan is forgiven"
BOUNTY_LOAN_FORGIVEN_NOTIFICATION_KEY = "Bounty loan forgiven"
# Notification - Bounty Loan Expired
BOUNTY_LOAN_EXPIRED_NOTIFICATION = (
    "Your loan of ฿{} from {} has expired."
    + BOUNTY_LOAN_EXPIRED_ACTION_PREFIX
    + BOUNTY_LOAN_EXPIRED_ACTION_BORROWER
)
BOUNTY_LOAN_EXPIRED_NOTIFICATION_DESCRIPTION = "If to be notified when your loan expires"
BOUNTY_LOAN_EXPIRED_NOTIFICATION_KEY = "Bounty loan expired"
# Notification - Warlord appointment
WARLORD_APPOINTMENT_NOTIFICATION = (
    "Congratulations, you have been appointed as a Warlord!\n\n*Epithet*:"
    " {}\n*Duration*: {}\n*Reason*: {}\n\n*Privileges*\n•"
    f" {Env.PIRATE_KING_TRANSACTION_TAX_DISCOUNT.get_int()}% off tax on gifts and"
    " loans\n• Immunity from Devil Fruit revocation for not appearing in the latest"
    f" {Env.DEVIL_FRUIT_MAINTAIN_MIN_LATEST_LEADERBOARD_APPEARANCE.get_int()} leaderboards\n•"
    " View inferior ranks status \\(Emperor and below\\)\n• Custom Bounty Poster"
    f" {Env.BOUNTY_POSTER_LIMIT_WARLORD.get_int()} times a day\n• View New World users"
    " in logs\n\n_You will appear in the weekly leaderboard exclusively with Warlord"
    " rank \\(only for the global leaderboard\\)_"
)
WARLORD_APPOINTMENT_NOTIFICATION_DESCRIPTION = (
    "If to be notified when you are appointed as a Warlord"
)
WARLORD_APPOINTMENT_NOTIFICATION_KEY = "Warlord appointment"
# Notification - Warlord revocation
WARLORD_REVOCATION_NOTIFICATION = "Your Warlord status has been revoked\n\n*Reason*: {}"
WARLORD_REVOCATION_NOTIFICATION_DESCRIPTION = (
    "If to be notified when your Warlord status is revoked"
)
WARLORD_REVOCATION_NOTIFICATION_KEY = "Warlord revocation"

# List
LIST_OVERVIEW = (
    "Select" + " {} *{}* from the list below\n{}"
)  # In the chunk to avoid IDE recognizing it as SQL
LIST_OVERVIEW_NO_ITEMS = "No {} found"
LIST_ITEM_TEXT = "\n*{}*. {}"
LIST_FOOTER = "\n\n_Showing {}-{} of {} items_"
LEGEND = "legend"
LIST_EMOJI_LEGEND = "\n\n_*Legend*{}_"
LIST_EMOJI_LEGEND_ITEM = "\n{} {} \\({}\\)"
LIST_FILTER_SEND_PART_OF_STRING = "\n\n__Send a part of the {} to restrict the search__"
LIST_FILTER_ACTIVE_FILTERS = "\n\n_*Active filters*:{}_"
LIST_FILTER_ITEM = "\n• {}"
LIST_FILTER_ITEM_CONTAINS = "{} contains '{}'"
LIST_FILTER_ONLY = "Only *{}*"
NAVIGATION_LIMIT_REACHED = "Limit reached"

# Logs
LOG_ITEM_DETAIL_GENERIC_OUTCOME_TEXT = "{} *{}*"
LOG_ITEM_DETAIL_GENERIC_OUTCOME_TEXT_NO_BOLD = "{} {}"
LOG_ITEM_DETAIL_OUTCOME_TEXT = "{}You *{}*"
LOG_ITEM_DETAIL_OUTCOME_BELLY_TEXT = "{}You *{}* ฿{}"
LOG_ITEM_DETAIL_STATUS_TEXT = "*Status*: {}"
LOG_ITEM_DETAIL_GO_TO_MESSAGE = (
    f"\n\n{Emoji.RIGHT_ARROW}[Go to message]("
    + "{}"
    + f"){Emoji.LEFT_ARROW}"
    + "\n_\\(The message may no longer be available\\)_"
)
LOG_ITEM_DETAIL_NO_PERMISSION = "You are not authorized to view this item"
LOG_STATS_TEXT = "*{} Statistics*\n\n{}"
LOG_STATS_NOT_ENOUGH_DATA = "Not enough data to generate statistics for this log"

# Logs - Fight
FIGHT_LOG_KEY = "Fights"
FIGHT_LOG_ITEM_DETAIL_TEXT_FILL_IN = "Fight"
FIGHT_LOG_ITEM_TEXT = "{} vs {} \\(฿{}\\)"
FIGHT_LOG_ITEM_DETAIL_TEXT = (
    f"*{{}}*: {{}}\n*Date*: {{}}\n*Win probability*: {{}}%\n\n{{}}{LOG_ITEM_DETAIL_GO_TO_MESSAGE}"
)
FIGHT_LOG_STATS_TEXT = (
    "*Total fights*: {}\n*Wins*: {} \\({}%\\)\n*Losses*: {} \\({}%\\)\n*Belly won*: ฿{}\n*Belly"
    " lost*: ฿{}\n*Max belly won*: [฿{} \\({}\\)]({})\n*Max belly lost*: [฿{} \\({}\\)]({})\n*Most"
    " fought user*: {} \\({}x\\)"
)

# Logs . Plunder
PLUNDER_LOG_KEY = "Plunders"
PLUNDER_LOG_ITEM_DETAIL_TEXT_FILL_IN = "Plunder"
PLUNDER_LOG_ITEM_TEXT = "{} vs {} \\(฿{}\\)"
PLUNDER_LOG_ITEM_DETAIL_TEXT = (
    f"*{{}}*: {{}}\n*Date*: {{}}\n*Win probability*: {{}}%\n\n{{}}{LOG_ITEM_DETAIL_GO_TO_MESSAGE}"
)
PLUNDER_LOG_ITEM_DETAIL_SENTENCE_DURATION = "\n\n*Impel Down sentence*: {}"
PLUNDER_LOG_STATS_TEXT = (
    "*Total plunders*: {}"
    "\n*Wins*: {} \\({}%\\)"
    "\n*Losses*: {} \\({}%\\)"
    "\n*Belly stole*: ฿{}"
    "\n*Belly lost*: ฿{}"
    "\n*Max belly stolen*: [฿{} \\({}\\)]({})"
    "\n*Max belly lost*: [฿{} \\({}\\)]({})"
    "\n*Max Impel Down sentence*: [{}]({})"
    "\n*Most plundered user*: {} \\({}x\\)"
)

# Logs - DocQ
DOC_Q_GAME_LOG_KEY = "Doc Q"
DOC_Q_GAME_LOG_ITEM_DETAIL_TEXT_FILL_IN = "Doc Q Game"
DOC_Q_GAME_LOG_ITEM_TEXT = "{} ฿{}"
DOC_Q_GAME_LOG_ITEM_DETAIL_TEXT = (
    f"*Date*: {{}}\n*Correct apple*: {{}}°\n\n{{}}{LOG_ITEM_DETAIL_GO_TO_MESSAGE}"
)
DOC_Q_GAME_LOG_STATS_TEXT = (  # Logs - Game
    "*Total summons*: {}\n*Wins*: {} \\({}%\\)\n*Losses*: {} \\({}%\\)\n*Belly won*: ฿{}\n*Belly"
    " lost*: ฿{}\n*Max belly won*: [฿{}]({})\n*Max belly lost*: [฿{}]({})\n"
)

GAME_LOG_KEY = "Challenges"
GAME_LOG_ITEM_DETAIL_TEXT_FILL_IN = "Challenge"
GAME_LOG_ITEM_TEXT = "{} vs {} \\(฿{}\\)"
GAME_LOG_ITEM_DETAIL_TEXT = (
    "*{}*: {}\n*Game*: {}\n*Date*: {}\n*Wager*:"
    f" ฿{{}}\n\n{{}}{LOG_ITEM_DETAIL_GO_TO_MESSAGE}"
)
GAME_LOG_STATS_TEXT = (
    "*Total challenges*: {}\n*Wins*: {} \\({}%\\)\n*Losses*: {} \\({}%\\)\n*Draws*: {}"
    " \\({}%\\)\n*Belly won*: ฿{}\n*Belly lost*: ฿{}\n*Max belly won*: [฿{} \\({}\\)]({})\n*Max"
    " belly lost*: [฿{} \\({}\\)]({})\n*Most challenged user*: {} \\({}x\\)\n*Most played game*:"
    " {} \\({}x\\)"
)

# Logs - Bounty Gift
BOUNTY_GIFT_LOG_KEY = "Bounty Gifts"
BOUNTY_GIFT_LOG_ITEM_DETAIL_TEXT_FILL_IN = "Bounty Gift"
BOUNTY_GIFT_LOG_ITEM_TEXT = "{} ฿{} {} {}"
BOUNTY_GIFT_LOG_ITEM_DETAIL_TAX_TEXT = "\n*Tax*: ฿{} \\({}%\\)\n*Total*: ฿{}"
BOUNTY_GIFT_LOG_ITEM_DETAIL_TEXT = (
    f"*{{}}*: {{}}\n*Date*: {{}}\n*Amount*: ฿{{}}{{}}{LOG_ITEM_DETAIL_GO_TO_MESSAGE}"
)
BOUNTY_GIFT_LOG_STATS_TEXT = (
    "*Total gifts*: {}\n*Total given*: ฿{}\n*Total received*: ฿{}\n*Highest given*: [฿{}"
    " \\({}\\)]({})\n*Highest received*: [฿{} \\({}\\)]({})\n*Top receiver*: {} \\(฿{}\\)\n*Top"
    " giver*: {} \\(฿{}\\)"
)
BOUNTY_GIFT_LOG_LEGEND_SENT = "Sent"
BOUNTY_GIFT_LOG_LEGEND_RECEIVED = "Received"

# Logs - Legendary Pirate
LEGENDARY_PIRATE_LOG_KEY = "Legendary Pirates"
LEGENDARY_PIRATE_LOG_ITEM_DETAIL_TEXT_FILL_IN = "Legendary Pirate"
LEGENDARY_PIRATE_LOG_ITEM_TEXT = "{}"
LEGENDARY_PIRATE_LOG_ITEM_DETAIL_TEXT = "*{}*\nEpithet: {}\n\n*Reason*: {}"

# Logs - Warlord
WARLORD_LOG_KEY = "Warlords"
WARLORD_LOG_ITEM_DETAIL_TEXT_FILL_IN = "Warlord"
WARLORD_LOG_ITEM_TEXT = "{}"
WARLORD_LOG_ITEM_DETAIL_TEXT = "*{}*\nEpithet: {}\n\n*Reason*: {}"

# Logs - New World Pirate
NEW_WORLD_PIRATE_LOG_KEY = "New World Pirates"
NEW_WORLD_PIRATE_LOG_ITEM_DETAIL_TEXT_FILL_IN = "New World Pirate"
NEW_WORLD_PIRATE_LOG_ITEM_TEXT = "{} \\(฿{}\\)"
NEW_WORLD_PIRATE_LOG_ITEM_DETAIL_CREW_TEXT = "\n*Crew*: {}"
NEW_WORLD_PIRATE_LOG_ITEM_DETAIL_TEXT = "*{}*\n\n*Bounty*: ฿{}\n*Location*: {}{}"

# Logs - Leaderboard Rank
LEADERBOARD_RANK_LOG_KEY = "Global Leaderboard Ranks"
LEADERBOARD_RANK_LOG_ITEM_DETAIL_TEXT_FILL_IN = "Global Leaderboard Rank"
LEADERBOARD_RANK_LOG_ITEM_TEXT = "Week {} of {} - {}"
LEADERBOARD_RANK_LOG_ITEM_DETAIL_TEXT = (
    "*Week {} of {}*\n\n*Position*: {}°\n*Rank*: {}\n*Bounty*: ฿{}"
)
LEADERBOARD_RANK_LOG_STATS_TEXT = (
    "*Total appearances*: {}\n*Appearances as Pirate King*: {} \\({}%\\)\n*Appearances as"
    " Emperor*: {} \\({}%\\)\n*Appearances as First Mate*: {} \\({}%\\)\n*Appearances as"
    " Supernova*: {} \\({}%\\)\n*Appearances as Warlord*: {} \\({}%\\)\n*Max rank*: [{}"
    " \\({}°\\)]({})\n*Max bounty*: [฿{} \\({}°\\)]({})"
)

# Logs - Income tax event
INCOME_TAX_EVENT_LOG_KEY = "Tax Breakdown"
INCOME_TAX_EVENT_LOG_ITEM_DETAIL_TEXT_FILL_IN = "Income Tax Breakdown"
INCOME_TAX_EVENT_LOG_ITEM_TEXT = "{} \\(฿{}\\)"
INCOME_TAX_EVENT_LOG_ITEM_DETAIL_TEXT = (
    "*Event*: [{}]({})\n*Date*: {}\n*Income*: ฿{}\n*Net gain*: "
    + Emoji.LOG_POSITIVE
    + "฿{}\n*Total tax*: "
    + Emoji.LOG_NEGATIVE
    + "฿{} \\({}%\\){}{}\n\n\n*Breakdown*{}"
)
INCOME_TAX_EVENT_LOG_ITEM_DETAIL_TEXT_DEDUCTION = "\n\n*Deductions*"
INCOME_TAX_EVENT_LOG_ITEM_DETAIL_TEXT_DEDUCTION_ITEM = "\n{}: {}%"
INCOME_TAX_EVENT_LOG_ITEM_DETAIL_TEXT_CONTRIBUTION = "\n\n*Contributions* \\(from tax\\)"
INCOME_TAX_EVENT_LOG_ITEM_DETAIL_TEXT_CONTRIBUTION_ITEM = "\n{}: ฿{} \\({}%\\)"

INCOME_TAX_EVENT_LOG_ITEM_DETAIL_TEXT_BREAKDOWN_ITEM = (
    "\n\nAmount: ฿{}\nGain: ฿{}\nTax: ฿{} \\({}%\\)"
)

SILENCE_ACTIVE = (
    "A soundproof field has been activated, only those who are granted permission can speak"
)
SILENCE_END = "The soundproof field has been cancelled, everyone can speak again"
SPEAK = "{} has been granted permission to speak"

# Devil Fruit
DEVIL_FRUIT_ABILITY_TEXT = "\n\n*Abilities*"
DEVIL_FRUIT_ABILITY_TEXT_LINE = "\n{}{} \\({}{}%\\)"
DEVIL_FRUIT_ABILITY_UNKNOWN = "\nUnknown"
# Devil Fruit - Private Chat
DEVIL_FRUIT_ITEM_TEXT = "{}"
DEVIL_FRUIT_ITEM_TEXT_FILL_IN = "Devil Fruit"
DEVIL_FRUIT_ITEM_DETAIL_TEXT = "*{}*\nCategory: {}{}{}{}"
DEVIL_FRUIT_ITEM_DETAIL_TEXT_EXPIRING_DATE = "\n\nExpiring in: {}"
DEVIL_FRUIT_ITEM_DETAIL_TEXT_SELL_COMMAND = (
    "\n\nYou can sell this Devil Fruit in the Chat Group with"
    f" {CommandName.DEVIL_FRUIT_SELL.get_formatted()} <price> command"
)
DEVIL_FRUIT_LIST_NO_ITEMS = "You do not have any Devil Fruits"
DEVIL_FRUIT_NOT_OWNER = "You do not own this Devil Fruit"
DEVIL_FRUIT_EAT_USER_ALREADY_ATE = "You have already eaten a Devil Fruit"
DEVIL_FRUIT_EAT_CONFIRMATION_REQUEST = (
    "Are you sure you want to eat the {}?{}\n\nYou will not be able to eat another Devil Fruit"
    " until you discard it"
)
DEVIL_FRUIT_EAT_CONFIRMATION_REQUEST_ABILITIES = "\nYou will gain the following abilities:\n{}"
DEVIL_FRUIT_EAT_CONFIRMATION_CONFIRMED = (
    "You have eaten the {} and gained the following abilities:\n{}"
)
DEVIL_FRUIT_DISCARD_CONFIRMATION_REQUEST = (
    "Are you sure you want to discard the {}?\n\nYou will lose it and can regain it by finding or"
    " trading for it again"
)
DEVIL_FRUIT_DISCARD_CONFIRMATION_CONFIRMED = "You have discarded the {}"
DEVIL_FRUIT_RELEASE_MESSAGE_INFO = (
    "Congratulations {}, you have found a Devil Fruit!\n\nName: *{}*\nCategory: {}{}"
    + DEVIL_FRUIT_EAT_OR_SELL
)

DEVIL_FRUIT_SELL_NO_AMOUNT = (
    "You need to specify the amount of belly you want to sell the Devil Fruit for\n\nExample:"
    f" {CommandName.DEVIL_FRUIT_SELL.get_formatted()} 10.000.000"
)
DEVIL_FRUIT_SELL_NO_FRUITS = (
    "You do not have any Devil Fruits that can be sold \\(only collected and non-eaten Devil"
    " Fruits can be sold\\)"
)
DEVIL_FRUIT_SELL_SELECT_FRUIT = (
    "Select the Devil Fruit you want to sell\n\n_Tip: When using this command in response to a"
    " user, only they will have the ability to purchase the Devil Fruit_"
)
DEVIL_FRUIT_SELL_NO_LONGER_OWN = "{} no longer owns this Devil Fruit"
DEVIL_FRUIT_SELL_NO_LONGER_SELLABLE = "This Devil Fruit is no longer sellable"
DEVIL_FRUIT_SELL_BUY = (
    "{} has put up the following Devil Fruit for sale:\n\n{}\n\nExpiring in: {}\n\nPrice:"
    " ฿{}\nTax: ฿{} \\({}%\\)\nTotal Price: ฿*{}*{}"
)
DEVIL_FRUIT_SELL_BUY_ONLY_BY_USER_ADDENDUM = "\n\n_Only {} can buy this Devil Fruit_"
DEVIL_FRUIT_SELL_BUY_NOT_ENOUGH_BELLY = "You do not have enough belly to buy this Devil Fruit"
DEVIL_FRUIT_SELL_BUY_CANNOT_BUY_OWN = "You cannot buy your own Devil Fruit"
DEVIL_FRUIT_SELL_BUY_SUCCESS = (
    "{} has bought the following Devil Fruit from {}\n\n{}\n\nExpiring in: *{}*\n\nPrice:"
    " ฿{}\nTax: ฿{} \\({}%\\)\nTotal Price: ฿*{}*"
)

# Admin chat error messages
NO_DEVIL_FRUIT_TO_SCHEDULE = "There are no {} Devil Fruits to schedule for release"

THANKS_FOR_ADDING_TO_GROUP = "Thanks for adding me to your Group!\n"

INCOME_TAX_EVENT_BOUNTY_LOAN = "Bounty Loan"
INCOME_TAX_EVENT_DEVIL_FRUIT_SELL = "Devil Fruit Sell"
INCOME_TAX_EVENT_PREDICTION = "Prediction"

INCOME_TAX_DEDUCTION_TYPE_ADMIN = "Admin"
INCOME_TAX_DEDUCTION_TYPE_CREW_ABILITY = "Crew Ability"
INCOME_TAX_DEDUCTION_TYPE_DEVIL_FRUIT = "Devil Fruit"

INCOME_TAX_CONTRIBUTION_TYPE_CREW_CHEST = "Crew Chest"

FEATURE_BOUNTY_GIFT = "Bounty Gift"
FEATURE_BOUNTY_MESSAGES_GAIN = "Bounty Messages Gain"
FEATURE_CHALLENGE = "Challenge"
FEATURE_CREW = "Crew"
FEATURE_DEVIL_FRUIT_APPEARANCE = "Devil Fruit Appearance"
FEATURE_DOC_Q = "Doc Q"
FEATURE_FIGHT = "Fight"
FEATURE_LEADERBOARD = "Leaderboard"
FEATURE_MESSAGE_FILTER = "Message Filter"
FEATURE_PREDICTION = "Prediction"
FEATURE_SILENCE = "Silence"
FEATURE_STATUS = "Status"
FEATURE_DEVIL_FRUIT_SELL = "Devil Fruit Sell"
FEATURE_BOUNTY_LOAN = "Bounty Loan"
FEATURE_PLUNDER = "Plunder"

# Ability
ABILITY_TYPE_DOC_Q_COOLDOWN_DURATION = "Doc Q Cooldown"
ABILITY_TYPE_GAME_COOLDOWN_DURATION = "Challenge Cooldown"
ABILITY_TYPE_FIGHT_COOLDOWN_DURATION = "Fight Cooldown"
ABILITY_TYPE_FIGHT_IMMUNITY_DURATION = "Fight Immunity"
ABILITY_TYPE_FIGHT_DEFENSE_BOOST = "Fight Defense Boost"
ABILITY_TYPE_PREDICTION_WAGER_REFUND = "Prediction wager fund max refund"
ABILITY_TYPE_GIFT_LOAN_TAX = "Gift and Loan Tax"
ABILITY_TYPE_INCOME_TAX = "Income Tax"
ABILITY_TYPE_PLUNDER_COOLDOWN_DURATION = "Plunder Cooldown"
ABILITY_TYPE_PLUNDER_IMMUNITY_DURATION = "Plunder Immunity"
ABILITY_TYPE_PLUNDER_SENTENCE_DURATION = "Plunder Sentence"


PLUNDER_CANNOT_PLUNDER_CREW_MEMBER = "You cannot plunder a member of your own Crew"
PLUNDER_CANNOT_PLUNDER_USER = "You cannot plunder this user"
PLUNDER_USER_IN_COOLDOWN = "Plunder cooldown active. You can plunder again in *{}*"
PLUNDER_CONFIRMATION_REQUEST = (
    "{} are you sure you want to steal from {}?\n"
    "\nIf you're successful, you will gain ฿*{}*."
    "\nIf you're caught, you will owe ฿*{}* and be jailed in Impel Down for *{}*!"
    + "\n\n_Success chance: *{}%*\nCurrent bounty: ฿*{}*\nFinal bounty if you win:"
    " ฿*{}*_\n\nIf you"
    " lose, a loan will be created to repay the penalty"
)
PLUNDER_WIN = (
    "{} have successfully robbed {}, better run away before they notice!\n\n" + GAME_WIN_STATUS
)
PLUNDER_LOSE = (
    "{} have been caught trying to rob {} and they have handed you over to the Marines."
    "\nYou will be jailed in Impel Down for *{}*, better luck next time!"
    + IMPEL_DOWN_RESTRICTION_PLACED_NOTIFICATION_DURATION_BAIL
    + "\n\nYou now have a [฿*{}* loan]({}) towards {}"
)
PLUNDER_LOSE_SENTENCE_REASON = "Failed plunder against {}"

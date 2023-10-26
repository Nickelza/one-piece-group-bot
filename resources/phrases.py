import resources.Environment as Env
import src.model.enums.Command as Command
from src.model.enums.Emoji import Emoji

COMMAND_NOT_IN_REPLY_ERROR = 'This command can only be used in a reply to a message'
COMMAND_IN_REPLY_TO_BOT_ERROR = "This command can't be used in reply to a bot"
COMMAND_IN_REPLY_TO_ERROR = "This command can't be used in a reply to your own message"
COMMAND_NOT_ACTIVE_ERROR = "This command is no longer available"
COMMAND_NOT_ACTIVE_WITH_REPLACEMENT_ERROR = COMMAND_NOT_ACTIVE_ERROR + '. ' + 'Please Use {} instead'
COMMAND_FOR_NEW_WORLD_USERS_ERROR = 'This command is only available for users in the New World'
COMMAND_FOR_USERS_AFTER_LOCATION_ERROR = 'This command is only available for users who have reached {}'
COMMAND_WHILE_ARRESTED_ERROR = 'This command is not available while you are arrested'
COMMAND_ONLY_BY_CREW_CAPTAIN_ERROR = 'This command is only available to Crew Captains'
COMMAND_NOT_IN_REPLY_TO_CREW_MEMBER_ERROR = 'This command can only be used in reply to a message from a Crew Member'
COMMAND_ONLY_BY_BOSS_ERROR = 'This command can only be used by an Admin, the Pirate King or a Legendary Pirate'
COMMAND_IN_REPLY_TO_ARRESTED_ERROR = "This command can't be used in reply to a message from an arrested user"
COMMAND_ONLY_BY_CHAT_ADMIN_ERROR = 'This command can only be used by a chat admin'
COMMAND_FEATURE_DISABLED_ERROR = 'This feature is currently disabled in this {}.' \
                                 f'\nYou can ask an Admin to enable via {Command.GRP_SETTINGS.get_formatted()}'
COMMAND_NOT_ALLOWED_FROM_DEEPLINK_ERROR = 'This command is not allowed from a deeplink'

SHOW_USER_STATUS = 'User: {}' \
                   '\nBounty: ฿*{}*{}' \
                   '\nRank: {}' \
                   '\nLocation: {}'
SHOW_USER_STATUS_FROZEN_BOUNTY = ' \\(Frozen\\)'
SHOW_USER_STATUS_RANK_PRISONER = Emoji.PRISONER + ' Prisoner'
SHOW_USER_STATUS_IMPEL_DOWN = 'Impel Down'
SHOW_USER_STATUS_PENDING_BOUNTY = '\nPending bounty: ฿*{}*'
SHOW_USER_STATUS_REMAINING_SENTENCE = '\nRemaining sentence: {}'
SHOW_USER_STATUS_PERMANENT_IMPEL_DOWN = 'Permanent'
SHOW_USER_STATUS_FIGHT_IMMUNITY = '\nFight immunity: {}'
SHOW_USER_STATUS_FIGHT_COOLDOWN = '\nFight cooldown: {}'
SHOW_USER_STATUS_CREW = '\nCrew: {}'
SHOW_USER_STATUS_BOUNTY_DAILY_BONUSES_TITLE = '\n\n*Daily Bounty Bonus*'
SHOW_USER_STATUS_BOUNTY_BONUSES_TEXT = '\n{}{} \\({}%\\)'
SHOW_USER_STATUS_BOUNTY_BONUS_CREW = 'Crew'
SHOW_USER_STATUS_BOUNTY_BONUS_CREW_MVP = 'Crew MVP'
SHOW_USER_STATUS_BOUNTY_BONUS_NEW_WORLD = 'New World'
SHOW_USER_STATUS_BOUNTY_DEDUCTIONS_TITLE = '\n\n*Bounty Deductions*'
SHOW_USER_STATUS_EXPIRED_LOAN = 'Expired loan'
SHOW_USER_STATUS_INCOME_TAX = 'Income tax'
SHOW_USER_STATUS_ADD_REPLY = '_Requested by {}_'
SHOW_USER_STATUS_DEVIL_FRUIT = '\n\n*Devil Fruit*\n_{}_{}'
NOT_ALLOWED_TO_VIEW_REPLIED_STATUS = 'You can only view the status of those who rank below you.' \
                                     '\n\n{} rank: {}' \
                                     '\n{} rank: {}'
ROOKIE_STATUS_PRIVATE_CHAT_ONLY = 'Rookies can only view their status in Private Chat'
PRISONER_STATUS_PRIVATE_CHAT_ONLY = 'Prisoners can only view their status in Private Chat'
STATUS_PRIVATE_CHAT_KEY = 'View in Private Chat'
BOUNTY_RESET = 'Bounties have been reset'

LEADERBOARD = '*{}* Leaderboard for week *{}* of *{}*\n\nHere are the top {} users with the most bounties:' \
              '{}' \
              '{}' \
              '\n\n_Next bounty reset on {} \\(in {}\\)_'
LEADERBOARD_ROW = '\n\n{}°: {}\n{} - ฿*{}*'
LEADERBOARD_LOCAL = 'Local'
LEADERBOARD_GLOBAL = 'Global'
LEADERBOARD_VIEW_GLOBAL_LEADERBOARD = '\n\n\n' + Emoji.GLOBE + '[Global Leaderboard]({})'

SAVE_MEDIA_NOT_IN_REPLY_TO_MEDIA = 'This command can only be used in a reply to a media message'
SAVED_MEDIA_UNKNOWN_TYPE = 'Unknown media type. Available types are: *{}*'
SAVE_MEDIA_SUCCESS = 'Media saved as *{}*'

GAME_WIN_LOSE_STATUS = '_Current bounty: ฿*{}*_' \
                       '\n_Final bounty if you win: ฿*{}*_' \
                       '\n_Final bounty if you lose: ฿*{}*_'
GAME_WIN_STATUS = "_You won ฿*{}*!_" \
                  "\n_Current bounty: ฿*{}*_"
GAME_LOSE_STATUS = "_You lost ฿*{}*!_" \
                   "\n_Current bounty: ฿*{}*_"

DOC_Q_GAME_NOT_ENOUGH_BOUNTY = 'You need a bounty of at least ฿*{}* to summon Doc Q.' \
                               '\n\n_Current bounty: ฿*{}*_'
DOC_Q_GAME_LIMIT_REACHED = 'You have reached the limit of Doc Q games. You can play again in *{}*'
DOC_Q_GAME_START = 'Hi {}, allow me to offer you an apple.' \
                   '\nIf you choose the right one, you will win ฿*{}*, else you will lose ฿*{}*.' \
                   '\nChoose wisely!' + '\n\n' + GAME_WIN_LOSE_STATUS

DOC_Q_GAME_NOT_FOUND = 'Doc Q game not found'
DOC_Q_GAME_CANCEL = 'See you next time!'
DOC_Q_GAME_WIN = "You're...haha...cough! cough! a really lucky one {}." \
                 "\nLet's go, Stronger...agh..!" + '\n\n{}' + GAME_WIN_STATUS
DOC_Q_GAME_LOSE = "Seems like today wasn't your lucky day {}...cough!...better luck next time." \
                  "\nLet's go, Stronger...agh..!" + '\n\n{}' + GAME_LOSE_STATUS

# Error messages
USER_NOT_FOUND = 'User not found'
UNRECOGNIZED_SCREEN = 'Unrecognized command'
SAVED_MEDIA_NOT_FOUND = 'Saved Media not found'
UNKNOWN_EXTRA_STEP = 'Unknown extra step'
PRIVATE_STEP_NOT_SET = 'Private step not set'
SAVED_USER_DATA_NOT_FOUND = 'Saved user data not found'

# Keyboard options
KEYBOARD_OPTION_CANCEL = Emoji.CANCEL + ' Cancel'
KEYBOARD_OPTION_DELETE = Emoji.DELETE + ' Delete'
KEYBOARD_OPTION_CLOSE = Emoji.CLOSE + ' Close'
KEYBOARD_OPTION_ACCEPT = Emoji.ACCEPT + ' Accept'
KEYBOARD_OPTION_REJECT = Emoji.REJECT + ' Reject'
KEYBOARD_OPTION_FIGHT = Emoji.FIGHT + ' Fight'
KEYBOARD_OPTION_RETREAT = Emoji.RETREAT + ' Retreat'
KEYBOARD_OPTION_BACK = Emoji.BACK + ' Back'
KEYBOARD_OPTION_YES = Emoji.YES + ' Yes'
KEYBOARD_OPTION_NO = Emoji.NO + ' No'

TEXT_YES = 'Yes'
TEXT_NO = 'No'
TEXT_WON = 'won'
TEXT_LOST = 'lost'
TEXT_IT_WAS = 'it was'
TEXT_THEY_WERE = 'they were'
TEXT_FROM = 'from'
TEXT_TO = 'to'
TEXT_TOPIC = 'Topic'
TEXT_GROUP = 'Group'
TEXT_NOT_SET = 'Not set'

EXCEPTION_CHAT_ID_NOT_PROVIDED = 'chat_id is None and update.effective_chat.id is None'
EXCEPTION_NO_EDIT_MESSAGE = 'new_message is False but update.callback_query is None'

KEYBOARD_NOT_FOUND = 'Keyboard not found'
KEYBOARD_USE_UNAUTHORIZED = 'You are not authorized to use this keyboard'

LOCATION_CHANGE_REGION_PROPOSAL = '{}{} would you like to move to {}?'
LOCATION_CHANGE_REGION_PROPOSAL_REJECTED = '{}{} You can move to {} later with {} command'
LOCATION_NEW_WORLD_REQUEST_REJECTED_NOT_ENOUGH_BOUNTY = 'You need a bounty of at least ฿*{}* to move to the New World.'
LOCATION_ALREADY_IN_REGION = 'You are already in {}'
LOCATION_CANNOT_CHANGE_REGION = 'You can change region in *{}*'
LOCATION_INVALID_CHANGE_REGION_REQUEST = 'Invalid region'

CHALLENGER = 'Challenger'
OPPONENT = 'Opponent'
SENDER = 'Sender'
RECEIVER = 'Receiver'

FIGHT_NOT_FOUND = 'Fight not found'
FIGHT_OPPONENT_NOT_FOUND = 'Opponent not found'
FIGHT_CANNOT_FIGHT_USER = "You can't fight this user"
FIGHT_CANNOT_FIGHT_CREW_MEMBER = "You can't fight a member of your Crew"
FIGHT_USER_IN_COOLDOWN = "Fight cooldown active. You can initiate a fight in *{}*"
FIGHT_CONFIRMATION_ODDS_RECALCULATED = "\n_*\\(Probability recalculated with opponent's Crew average bounty\\)*_"
FIGHT_CONFIRMATION_REQUEST = '{} are you sure you want to fight {}?' \
                             '\nI predict a {}% probability of {}.' + '{}\n\n' + GAME_WIN_LOSE_STATUS
FIGHT_CONFIRMATION_OUTCOME_VICTORY = 'victory'
FIGHT_CONFIRMATION_OUTCOME_DEFEAT = 'defeat'
FIGHT_WIN = "Just as I foresaw, {} won the fight against {}.\n" \
            "I don't need the cards to tell me that your strength is incredible..." + '\n\n' + GAME_WIN_STATUS
FIGHT_LOSE = "Just as I foresaw, {} lost the fight against {}.\n" \
             "Looks like your luck ran out..." + '\n\n' + GAME_LOSE_STATUS
FIGHT_CONFIRMATION_RETREAT = 'You have successfully retreated'

ENABLED = Emoji.ENABLED + ' Enabled'
DISABLED = Emoji.DISABLED + ' Disabled'
CURRENT_SETTING = 'Current setting: {}'

INLINE_QUERY_SEND_ITEM = 'Send item'

# General
KEY_MANAGE = 'Manage'
KEY_CREATE = Emoji.CREATE + ' Create'
KEY_SAVE = Emoji.SAVE + ' Save'
KEY_ENABLE = Emoji.ENABLED + ' Enable'
KEY_DISABLE = Emoji.DISABLED + ' Disable'
KEY_OPEN = 'Open'
KEY_CLOSE = Emoji.CLOSE + ' Close'
KEY_SHARE = Emoji.SHARE + ' Share'
KEY_SEND_TO_GROUP = Emoji.GROUP + ' Send to group'
KEY_SET_RESULT = 'Set result'
KEY_CONFIRM = 'Confirm'

# Private chat
PVT_TXT_START = f'Welcome to One Piece Group Bot, a Bot that brings the Bounty System to any Chat Group!' \
                f'\nWhat would you like to do?'
PVT_KEY_SETTINGS = Emoji.SETTINGS + ' Settings'
PVT_KEY_STATUS = Emoji.STATUS + ' Status'
PVT_TXT_SETTINGS = 'Which setting would you like to change?'
PVT_KEY_SETTINGS_LOCATION_UPDATE = 'Location update'
PVT_TXT_SETTINGS_LOCATION_UPDATE = 'Do you want to receive an update when you move to a new location?'
PVT_KEY_CREW = Emoji.CREW + ' Crew'
PVT_KEY_CREW_LEAVE = 'Leave'
PVT_KEY_CREW_EDIT_NAME = 'Edit name'
PVT_KEY_CREW_DISBAND = 'Disband'
PVT_KEY_CREW_MEMBER_REMOVE = 'Remove'
PVT_KEY_SETTINGS_NOTIFICATIONS = 'Notifications'
PVT_TXT_SETTINGS_NOTIFICATIONS = 'Which category of notifications would you like to change?'
PVT_TXT_SETTINGS_NOTIFICATIONS_TYPE = 'Which notification would you like to change?'
PVT_KEY_MANAGE_NOTIFICATION_SETTINGS = 'Manage notification settings'
PVT_KEY_SETTINGS_TIMEZONE = 'Time zone'
PVT_TXT_SETTINGS_TIMEZONE = '\nCurrent time: *{}*' \
                            '\nCurrent timezone: *{}* \\({}\\)' \
                            '\n\nTo set a new time zone, send a location name \\(city, region, state or country\\)'
PVT_TXT_SETTINGS_TIMEZONE_INVALID = 'Invalid location. Please send a correct location name ' \
                                    '\\(city, region, state or country\\)'
PVT_KEY_SETTINGS_TIMEZONE_RESET = 'Reset'
PVT_TXT_SETTINGS_TIMEZONE_UNKNOWN = 'Default - ' + Env.TZ.get()

PVT_KEY_LOGS = Emoji.LOGS + ' Logs'
PVT_TXT_LOGS = 'Which log would you like to view?'
PVT_KEY_LOGS_STATS = Emoji.STATS + ' Stats'
PVT_KEY_PREVIOUS_PAGE = Emoji.LEFT_ARROW
PVT_KEY_NEXT_PAGE = Emoji.RIGHT_ARROW
PVT_KEY_PREDICTION = Emoji.PREDICTION + ' Predictions'
PVT_KEY_PREDICTION_DETAIL_PLACE_BET = 'Place bet'
PVT_KEY_PREDICTION_DETAIL_REMOVE_BET = 'Remove bet'
PVT_KEY_PREDICTION_DETAIL_EDIT = 'Edit'
PVT_KEY_PREDICTION_CREATE_ALLOW_MULTIPLE_CHOICES = 'Allow multiple choices'
PVT_KEY_PREDICTION_CREATE_ALLOW_BET_WITHDRAWAL = 'Allow bet withdrawal'
PVT_KEY_PREDICTION_CREATE_IS_PUBLIC = 'Public'
PVT_KEY_PREDICTION_CREATE_SET_CLOSE_DATE = Emoji.PREDICTION_CLOSED + ' Set closing date'
PVT_KEY_PREDICTION_CREATE_REMOVE_CLOSE_DATE = Emoji.PREDICTION_CLOSED + ' Remove closing date'
PVT_KEY_PREDICTION_CREATE_SET_CUT_OFF_DATE = Emoji.PREDICTION_CUT_OFF + ' Set cut-off date'
PVT_KEY_PREDICTION_CHANGE_POLL = Emoji.CHANGE + ' Change poll'
PVT_KEY_PREDICTION_NO_CORRECT_OPTION = 'No correct option'
PVT_KEY_DEVIL_FRUIT = Emoji.DEVIL_FRUIT + ' Devil Fruit'
PVT_KEY_DEVIL_FRUIT_DETAIL_EAT = 'Eat'
PVT_KEY_DEVIL_FRUIT_DETAIL_TRADE = 'Trade'
PVT_KEY_DEVIL_FRUIT_DETAIL_DISCARD = 'Discard'
PVT_KEY_GO_TO_MESSAGE = 'Go to message'
PVT_KEY_BOUNTY_LOAN = Emoji.MONEY + ' Loan'
PVT_KEY_BOUNTY_LOAN_DETAIL_PAY = 'Pay'
PVT_KEY_BOUNTY_LOAN_DETAIL_FORGIVE = 'Forgive'

GRP_KEY_DEVIL_FRUIT_BUY = Emoji.MONEY + ' Buy'
GRP_TXT_SETTINGS = '{}Which Bounty System features would you like to enable in this {}?'
GRP_KEY_GO_TO_MESSAGE = 'Go to message'
GRP_KEY_PREDICTION_BET_IN_PRIVATE_CHAT = 'Bet in private chat'
GRP_KEY_PREDICTION_VIEW_IN_PRIVATE_CHAT = 'View in private chat'
GRP_KEY_GAME_PLAY = 'Play'

DATETIME_EXAMPLES = '''
Write the date using this format:
dd/mm/yy hh:mm

*Examples*:
• 1/4/2022 22:30
• in 10 days 5 hours 2 minutes
• Tomorrow at 12:00

Current time: *{}*
Current time zone: *{}* \\({}\\)
[Change time zone]({})
'''.strip()

DATETIME_EXAMPLES_NO_DURATION = '''
Write the date using this format:
dd/mm/yy hh:mm

*Examples*:
• 1/4/2022 22:30
• 10 hours ago
• Yesterday at 12:00

Current time: *{}*
Current time zone: *{}* \\({}\\)
[Change time zone]({})
'''.strip()

ACTION_INSUFFICIENT_BOUNTY = "Insufficient bounty"
ACTION_WAGER_LESS_THAN_MIN = "The minimum amount is ฿*{}*"
ACTION_INVALID_WAGER_AMOUNT = "Invalid amount. " \
                              "Make sure it is a number with only '.' or ',' as decimal separator or with a valid " \
                              "magnitude." \
                              "\n\nExample: " \
                              "\n- 10.000.000 or 10,000,000" \
                              "\n- 10k, 10thousand, 10m, 10million, 10b, 10billion"
ACTION_INVALID_DURATION = "Invalid duration. " \
                          "Make sure it is a number with only '.' or ',' as decimal separator or with a valid " \
                          "unit." \
                          "\n\nExample: " \
                          "\n - 1min, 1h, 1d, 1week"

GAME_CANNOT_CHALLENGE_USER = "You can't challenge this user"
GAME_CHOOSE_GAME = 'Which game would you like to play?'
GAME_NO_WAGER_AMOUNT = 'You need to specify a wager amount.' \
                       f'\n\nExample: {Command.GRP_GAME.get_formatted()} 10.000.000'

GAME_NOT_FOUND = 'Game not found'
GAME_REQUEST = '{}, you have been challenged by {} to play *{}* with a wager of ฿*{}*.' \
               '\n\n_*Description*: {}_' \
               '\n\nWould you like to accept?' \
               f'\n\nIf the challenge is not accepted within {Env.GAME_CONFIRMATION_TIMEOUT.get_int()} seconds, ' \
               f'it will be automatically rejected.'
GAME_REQUEST_OPEN = '{} is challenging anyone to play *{}* with a wager of ฿*{}*.' \
                    '\n\nPress the button below to accept.' \
                    f'\n\nIf the challenge is not accepted within {Env.GAME_CONFIRMATION_TIMEOUT.get_int()} seconds, ' \
                    f'it will be automatically rejected.'
GAME_CANCELED = 'Game cancelled'
GAME_CHALLENGE_REJECTED = '{} has rejected the challenge'
GAME_INVALID = 'Invalid game'
GAME_NOT_SELECTED_NAME = 'Not selected'
GAME_TEXT = '*{}*' \
            '\n\n_*Description*: {}_' \
            '\n\n{} vs {}' \
            '\nWager: ฿*{}*' \
            '{}' \
            '\n\n{}'
GAME_STATUS_AWAITING_CHOICE = 'Status: Awaiting choice'
GAME_STATUS_AWAITING_USER_CHOICE = "Status: Awaiting {}'s choice"
GAME_RESULT_DRAW = 'Result: Draw'
GAME_RESULT_WIN = Emoji.WINNER + ' {} won'
GAME_NOT_YOUR_TURN = "It's not your turn"
GAME_TURN = "Status: {}'s turn"
GAME_ENDED = 'This game has ended'
GAME_CANNOT_INITIATE = 'Challenge limit reached, make sure you have canceled any pending challenges.' \
                       '\nYou can initiate another challenge in *{}*, but in the meantime you can ask another user ' \
                       'to challenge you.'
GAME_PENDING_KEY = 'Pending challenge'
GAME_FORCED_END = 'This game has ended due to bounty reset or inactivity. The wagers has been returned to the players.'

GAME_STATUS_ND = 'Not defined'
GAME_STATUS_IN_PROGRESS = 'In progress'
GAME_STATUS_WON = 'Won'
GAME_STATUS_LOST = 'Lost'
GAME_STATUS_DRAW = 'Draw'
GAME_STATUS_AWAITING_SELECTION = 'Awaiting game selection'
GAME_STATUS_AWAITING_OPPONENT_CONFIRMATION = 'Awaiting opponent confirmation'
GAME_STATUS_FORCED_END = 'Forced end due to bounty reset'
GAME_STATUS_COUNTDOWN_TO_START = 'Countdown to start'
GAME_COUNTDOWN = 'The game will start in *{}*'
GAME_STARTED = 'Game in progress'
GAME_TIMEOUT = 'This game was canceled due to timeout while awaiting opponent confirmation.' \
               '\n\nThe wager has been returned to the challenger.'
GAME_INPUT_NOT_PLAYER = 'You are not a player of this game'
GAME_INPUT_GAME_FINISHED = 'This game has ended'
GAME_INPUT_COUNTDOWN = 'The game has not started yet.\nStay on this chat as to not miss the first message!'
GAME_RESULT_CHARACTER = 'Character: {}'
GAME_RESULT_TERM = 'Word: {}'
GAME_DIFFICULTY = '\nDifficulty: {}'
GAME_DIFFICULTY_EASY = 'Easy'
GAME_DIFFICULTY_MEDIUM = 'Medium'
GAME_DIFFICULTY_HARD = 'Hard'

ROCK_PAPER_SCISSORS_GAME_NAME = 'Rock Paper Scissors'
ROCK_PAPER_SCISSORS_GAME_DESCRIPTION = 'Try to beat your opponent by choosing rock, paper or scissors. ' \
                                       '\nRock beats scissors, scissors beats paper and paper beats rock.'
ROCK_PAPER_SCISSORS_CHOICE_ALERT = 'You chose {}'
ROCK_PAPER_SCISSORS_CHOICE_ROCK = Emoji.ROCK + ' Rock'
ROCK_PAPER_SCISSORS_CHOICE_PAPER = Emoji.PAPER + ' Paper'
ROCK_PAPER_SCISSORS_CHOICE_SCISSORS = Emoji.SCISSORS + ' Scissors'
ROCK_PAPER_SCISSORS_CHOICES = '{} chose {} ' \
                              '\n{} chose {}\n\n'

RUSSIAN_ROULETTE_GAME_NAME = 'Russian Roulette'
RUSSIAN_ROULETTE_GAME_DESCRIPTION = 'Try to avoid choosing the chamber with the bullet.'

RUSSIAN_ROULETTE_GAME_CHAMBER_ALREADY_FIRED = 'This chamber has already been fired. Choose another one.'
RUSSIAN_ROULETTE_GAME_BULLET_SHOT = "You've died"
RUSSIAN_ROULETTE_GAME_BULLET_NOT_SHOT = "You've survived another round"

GUESS_GAME_INPUT_CAPTION_HINT = '\n\n' + Emoji.NEW + 'Hint: {}'
GUESS_GAME_INPUT_CAPTION_SECONDS_TO_NEXT_HINT = '\n\nIn *{}* seconds, a hint will be sent'
GUESS_GAME_INPUT_CAPTION_SECONDS_TO_NEXT_IMAGE = '\n\nIn *{}* seconds, an easier variation will be sent'
GUESS_GAME_INPUT_CAPTION_SECONDS_TO_NEXT_LIFE_1 = 'In *{}* seconds, a new life will be issued'
GUESS_GAME_INPUT_CAPTION_SECONDS_TO_NEXT_LIFE_2 = 'A new life will be issued every {} seconds'
GUESS_GAME_INPUT_CAPTION_SECONDS_TO_NEXT_DETAIL = '\n\nIn *{}* seconds, a new detail will be given'

GUESS_CHARACTER_GAME_INPUT_CAPTION = 'Send your guesses as text messages, you will be notified if you are correct. ' \
                                     f'\nThe name must be the same as the one used on ' \
                                     f'[One Piece Wiki]({Env.ONE_PIECE_WIKI_URL.get()})'
GUESS_TERM_GAME_INPUT_CAPTION = 'Send your guesses as text messages, you will be notified if you are correct. ' \
                                f'\nThe term must be the same as the one used on ' \
                                f'[One Piece Wiki]({Env.ONE_PIECE_WIKI_URL.get()})'
GUESS_GAME_CORRECT_ANSWER = f'Congratulations, you guessed correctly{Emoji.CONFETTI}' \
                            '\n\n{}'
GUESS_GAME_OPPONENT_CORRECT_ANSWER = f'Oops, your opponent was able to guess before you😔' \
                                     f'\nBetter luck next time!' \
                                     '\n\n{}'

WHOS_WHO_GAME_NAME = "Who's Who"
WHOS_WHO_GAME_DESCRIPTION = 'Guess the blurred character. ' \
                            '\nEvery {} seconds, a less blurred image will be sent until the character is fully ' \
                            'revealed.' \
                            '\nThis game is played in private chat with the Bot.'

SHAMBLES_GAME_NAME = 'Shambles'
SHAMBLES_GAME_DESCRIPTION = 'Guess the One Piece related word from a crossword puzzle. ' \
                            '\nEvery {} seconds, an extra letter will be removed from the puzzle making it easier to ' \
                            'guess.' \
                            '\nThis game is played in private chat with the Bot.'

GUESS_OR_LIFE_GAME_NAME = 'Guess or Life'
GUESS_OR_LIFE_GAME_DESCRIPTION = 'Guess the missing letters of the One Piece related word, any wrong guess will cost ' \
                                 'a life.' \
                                 '\nA new life will be issued every {} seconds.'
GUESS_OR_LIFE_GAME_LETTER_ALREADY_USED = f'{Emoji.WARNING} You have already used this letter'
GUESS_OR_LIFE_GAME_NO_MORE_LIVES = f'{Emoji.WARNING} You have no more lives left'
GUESS_OR_LIFE_GAME_CORRECT_LETTER = f'{Emoji.CORRECT} Correct letter!'
GUESS_OR_LIFE_GAME_WRONG_LETTER = f'{Emoji.LOG_NEGATIVE} Wrong letter'
GUESS_OR_LIFE_GAME_WORD_LIVES = '{}' \
                                '{}\nLives: {}{}'
GUESS_OR_LIFE_GAME_NAME_WORD = '*{}*' \
                               '\n{}'
GUESS_OR_LIFE_GAME_NAME_WORD_LIVES = '*{}*' \
                                     '\n' + GUESS_OR_LIFE_GAME_WORD_LIVES
GUESS_OR_LIFE_GAME_REMAINING_USED_LETTERS = '\n\nRemaining letters: {}' \
                                            '\n\nUsed letters: {}'
GUESS_OR_LIFE_GAME_PRIVATE_RECAP = '{}\n\n{}'
GUESS_OR_LIFE_GAME_INPUT_CAPTION_ONE_LETTER = f'{Emoji.WARNING}Please send only one letter at a time'
GUESS_OR_LIFE_GAME_INPUT_CAPTION_LETTER_ONLY = f'{Emoji.WARNING}Please send only letters (no numbers or symbols)'

PUNK_RECORDS_GAME_NAME = 'Punk Records'
PUNK_RECORDS_GAME_DESCRIPTION = 'Guess the One Piece related character from details about them. ' \
                                '\nEvery {} seconds, a new detail will be revealed making it easier to guess.' \
                                '\nThis game is played in private chat with the Bot.'
PUNK_RECORDS_GAME_RECAP = '{}' \
                          '{}'
PUNK_RECORDS_GAME_RECAP_DETAIL = '\n{}*{}*: {}'
PUNK_RECORDS_GAME_RECAP_DETAIL_LIST = '\n*{}*' \
                                      '\n{}'

PREDICTION_NOT_FOUND = 'Prediction not found'
PREDICTION_NOT_IN_NEW_STATUS = 'Prediction not in NEW status'
PREDICTION_NOT_SENT = 'Prediction not sent'
PREDICTION_NOT_IN_SENT_STATUS = 'Prediction not in SENT status'
PREDICTION_NOT_IN_BETS_CLOSED_STATUS = 'Prediction not in BETS\\_CLOSED status'
UNKNOWN_PREDICTION_ACTION = 'Unknown prediction action'
PREDICTION_TEXT = '*{}*' \
                  '\n{}' \
                  '\n\n*Total wager*: ฿{}' \
                  '\n*Status*: {}' \
                  '{}{}{}{}'
PREDICTION_CREATE_RECAP = '*{}*' \
                          '\n{}' \
                          '{}'
PREDICTION_TEXT_OPTION = '\n{}. {}'
PREDICTION_TEXT_OPTION_WITH_PERCENTAGE = PREDICTION_TEXT_OPTION + ' \\(*{}%*\\){}'
PREDICTION_CLOSING_DATE = '\n*Closing date*: {}'
PREDICTION_CUT_OFF_DATE = '\n*Cut off date*: {}'
PREDICTION_WAGERS_REFUNDED = '\n{} Wagers refunded{}'
PREDICTION_WAGERS_REFUNDED_MAX = ' \\(max. ฿{}\\)'
PREDICTION_MULTIPLE_BETS_ALLOWED = '\n{} Multiple bets allowed'
PREDICTION_MULTIPLE_BETS_ALLOWED_DESCRIPTION = '\n_\\(Users can bet on multiple options\\)_'
PREDICTION_CAN_WITHDRAW_BETS = '\n{} Can withdraw bets'
PREDICTION_CAN_WITHDRAW_BETS_DESCRIPTION = '\n_\\(Users can withdraw their bets before the prediction is closed\\)_'
PREDICTION_IS_PUBLIC = '\n{} Public'
PREDICTION_IS_PUBLIC_DESCRIPTION = '\n_\\(Anyone in your groups can find this prediction.' \
                                   '\nIf disabled, only those who you share the prediction with can view it.' \
                                   '\nYour fellow Crew members will always be able to find it._\\)'
PREDICTION_BET_INVALID_FORMAT = 'Make sure your bet is in the following format:' \
                                f'\n{Command.GRP_PREDICTION_BET.get_formatted()} <amount> <option number>' \
                                f'\n\nExample: {Command.GRP_PREDICTION_BET.get_formatted()} 10.000.000 1'
PREDICTION_BET_HOW_TO_PLACE_BET = '\n\n_To place a bet, reply to this message with the following command:' \
                                  f'\n{Command.GRP_PREDICTION_BET.get_formatted()} <amount> <option number>' \
                                  f'\nExample: {Command.GRP_PREDICTION_BET.get_formatted()} 10.000.000 1_'
PREDICTION_BET_HOW_TO_REMOVE_BET = '\n\n_To remove a bet, reply to the prediction with the following command:' \
                                   f'\n{Command.GRP_PREDICTION_BET_REMOVE.get_formatted()} <option number>' \
                                   f'\nExample: {Command.GRP_PREDICTION_BET_REMOVE.get_formatted()} 1_'
PREDICTION_BET_HOW_TO_REMOVE_ALL_BETS = '\n\n_To remove all bets, reply to the prediction with the following command:' \
                                        f'\n{Command.GRP_PREDICTION_BET_REMOVE.get_formatted()}_'
PREDICTION_BET_HOW_TO_VIEW_BET_STATUS = '\n\n_To view your bet status, reply to the prediction with the following ' \
                                        'command:' \
                                        f'\n{Command.GRP_PREDICTION_BET_STATUS.get_formatted()}_'

PREDICTION_CLOSED_FOR_BETS = 'This prediction no longer accept bets'
PREDICTION_NOT_FOUND_IN_REPLY = 'Prediction not found in replied message. Make sure you replied to a prediction ' \
                                'or the prediction might have been deleted.'
PREDICTION_ALREADY_BET = 'You have already bet on this prediction'
PREDICTION_ALREADY_BET_ON_OPTION = 'You have already bet on this option'
PREDICTION_OPTION_NOT_FOUND = 'Option *{}* not found in prediction'
PREDICTION_BET_SUCCESS = 'Bet placed successfully'
PREDICTION_RESULTS_SET = 'The results of this prediction have been set'
PREDICTION_BET_REMOVE_INVALID_FORMAT = 'Make sure your command is in the following format:' \
                                       f'\n{Command.GRP_PREDICTION_BET_REMOVE.get_formatted()} ]<option number>' \
                                       f'\n\nExample: {Command.GRP_PREDICTION_BET_REMOVE.get_formatted()} 1'
PREDICTION_BET_REMOVE_SUCCESS = 'Bet removed successfully'
PREDICTION_BET_USER_HAS_NOT_BET = 'You have not bet on this prediction'
PREDICTION_BET_REMOVE_ALL_SUCCESS = 'All your bets on this prediction have been removed successfully'
PREDICTION_CLOSED_FOR_BETS_REMOVAL = 'You can no longer withdraw bets from this prediction'
PREDICTION_DOES_NOT_ACCEPT_BETS_WITHDRAWAL = 'This prediction does not accept bets withdrawal'
PREDICTION_OPTION_NOT_BET_ON = 'You have not bet on this option'
PREDICTION_STATUS_BETS_HEADER = '*Bets*'
PREDICTION_STATUS_OPTION = '\n\n*{}*. {} ' \
                           '\n*Amount*: ฿{}'
PREDICTION_STATUS_POTENTIAL_WIN = '\n*Potential win*: ฿{}'
PREDICTION_STATUS_RESULT_LOST = '\n*Result*: ' + Emoji.PREDICTION_BET_LOSE + 'Lost'
PREDICTION_STATUS_RESULT_LOSS_REFUNDED = ' \\(Refunded\\)'
PREDICTION_STATUS_RESULT_WIN = '\n*Result*: ' + Emoji.PREDICTION_BET_WIN + '฿{}'
PREDICTION_STATUS_TOTAL_WIN = '\n\n*Total win*: ' + Emoji.PREDICTION_BET_WIN + '฿{}'
PREDICTION_STATUS_NET_WIN = '\n\n*Net win*: ' + Emoji.PREDICTION_BET_WIN + '฿{}'
PREDICTION_STATUS_TOTAL_LOSS = '\n\n*Total loss*: ' + Emoji.PREDICTION_BET_LOSE + '฿{}'
PREDICTION_STATUS_NET_LOSS = '\n\n*Net loss*: ' + Emoji.PREDICTION_BET_LOSE + '฿{}'
PREDICTION_ALL_BETS_REMOVED_FOR_BOUNTY_RESET = 'All bets have been removed from this prediction due to bounty reset'
# Prediction Private Chat
PREDICTION_ITEM_TEXT = '{} {}'
PREDICTION_ITEM_TEXT_FILL_IN = 'Prediction'
PREDICTION_ITEM_DETAIL_TEXT = '{}\n\n{}'
PREDICTION_PLACE_BET_TEXT = '{}'
PREDICTION_PLACE_BET_DETAIL_TEXT = '*Question*: {}' \
                                   '\n\n*Option*: {}' \
                                   '\n\n_Please send the amount you want to bet_'
PREDICTION_PLACE_BET_LIST_OVERVIEW = 'On which option do you want to place a bet?\n{}'
PREDICTION_REMOVE_BET_TEXT = '{}'
PREDICTION_REMOVE_BET_LIST_OVERVIEW = 'From which option do you want to remove your bet?\n{}'
PREDICTION_CREATE_COOLDOWN_ACTIVE = 'You can create a prediction in *{}*'
PREDICTION_CREATE_REQUEST_POLL = 'Send the prediction as a Telegram poll with the question and options'
PREDICTION_CREATE_INVALID_POLL = 'Invalid poll. Make sure to send a Telegram poll with a question and at least ' \
                                 'two options'
PREDICTION_CAN_EDIT_POLL_ONLY_IF_NEW = 'You can only edit the question and options if the prediction if the ' \
                                       'prediction has not been enabled yet'
PREDICTION_CREATE_REQUEST_CLOSE_DATE = 'Send the closing date of the prediction.\n\n' + DATETIME_EXAMPLES
PREDICTION_CREATE_INVALID_CLOSE_DATE = 'Invalid closing date. Make sure to send a valid date.\n\n' + DATETIME_EXAMPLES
PREDICTION_CREATE_INVALID_CLOSE_DATE_PAST = 'Invalid closing date. Make sure to send a date in the future.\n\n' \
                                            + DATETIME_EXAMPLES
PREDICTION_CREATE_REQUEST_CUT_OFF_DATE = 'Send the cut off date of the prediction.' \
                                         '\nAll bets placed after this time will be removed and refunded.' \
                                         '\nThis action cannot be undone.' \
                                         '\nThe time must be after the prediction was opened and before it was ' \
                                         'closed or any previously set cut off time' \
                                         '\n\n*Opened time*: {}' \
                                         '\n*Closed time*: {}' \
                                         '\n*Cut off time*: {}' \
                                         '\n\n' + DATETIME_EXAMPLES_NO_DURATION
PREDICTION_CREATE_INVALID_CUT_OFF_DATE = 'Invalid cut off date. Make sure to send a valid date and time after the ' \
                                         'prediction was opened and before it was closed or any previously set cut ' \
                                         'off time.' \
                                         '\n\n*Opened time*: {}' \
                                         '\n*Closed time*: {}' \
                                         '\n*Cut off time*: {}' \
                                         '\n\n' + DATETIME_EXAMPLES_NO_DURATION
PREDICTION_CUT_OFF_DATE_CONFIRMATION_REQUEST = 'Are you sure you want to set the cut off date to *{}*?' \
                                               '\n{} bets with a total of ฿{} will be removed'
PREDICTION_SETTING_CANNOT_BE_CHANGED = 'This setting cannot be changed'
PREDICTION_CREATE_CLOSE_DATE = PREDICTION_CLOSING_DATE \
                               + '\n_\\(If set, the prediction will be automatically closed to new bets at this ' \
                                 'date\\)_'
PREDICTION_CREATE_CUT_OFF_DATE = '\n' + PREDICTION_CUT_OFF_DATE \
                                 + '\n_\\(If set, all bets placed after this time will be removed and refunded\\)_'
PREDICTION_CUT_OFF_DATE_HOW_TO_SET = '\n_You can set it from the edit menu_'
PREDICTION_USER_DISCLAIMER = '\n\n_This prediction was created by a regular user and is not endorsed by the ' \
                             'Bounty System Staff. Make sure to trust the creator before placing a bet._'
PREDICTION_DELETE_CONFIRMATION = 'Are you sure you want to delete this prediction? This action cannot be undone.' \
                                 '\nYou will be able to create another prediction in *{}*.' \
                                 '\n\nIf someone has placed a bet on this prediction, they will be refunded.'
PREDICTION_OPEN_CONFIRMATION = 'Are you sure you want to open this prediction? You will not be able to change the ' \
                               'question or options after this.' \
                               '\n\nIf the prediction is public, anyone in your groups will be able to find it.' \
                               '\nYour fellow Crew members will always be able to find it.'
PREDICTION_CREATE_SUCCESS = 'Prediction created successfully'
PREDICTION_DELETE_SUCCESS = 'Prediction deleted successfully'
PREDICTION_OPEN_SUCCESS = 'Prediction now open for bets'
PREDICTION_ALREADY_OPEN = 'Prediction already open for bets'
PREDICTION_ALREADY_CLOSED = 'Prediction already closed for bets'
PREDICTION_CLOSE_CONFIRMATION = 'Are you sure you want to close this prediction to new bets?' \
                                '\nThis action cannot be undone.'
PREDICTION_CLOSE_SUCCESS = 'Prediction closed successfully'
PREDICTION_INLINE_RESULT_SHARE = 'Share Prediction'
PREDICTION_IN_WRONG_STATUS = 'Prediction in wrong status'
PREDICTION_SEND_TO_GROUP = 'You can send this prediction to groups or topics where you are an Admin and users will ' \
                           'be able to bet on it by replying to the message.' \
                           '\nIf you don\'t find a group, make sure the Bot is a member of the group and use the ' \
                           f'{Command.PVT_USER_STATUS.get_formatted()} command in the group.' \
                           '\nYou can send only once to each group or topic.{}'
PREDICTION_SEND_TO_GROUP_NO_GROUPS = '\n\n_No groups found_'
PREDICTION_SEND_TO_GROUP_GROUPS_AVAILABLE = '*\n\nAvailable*:{}' \
                                            '\n\nSelect the number of the group \\(no confirmation is required\\)'
PREDICTION_SEND_TO_GROUP_GROUPS_ALREADY_SENT = '*\n\nAlready sent*:{}'
PREDICTION_SEND_TO_GROUP_GROUPS_ALREADY_SENT_ITEM = '\n•{}'
PREDICTION_SEND_TO_GROUP_GROUPS_AVAILABLE_ITEM = '\n{}. {}'
PREDICTION_SEND_TO_GROUP_NOT_ADMIN = 'You are no longer an Admin'
PREDICTION_SEND_TO_GROUP_ALREADY_SENT = 'This prediction has already been sent to this group'
PREDICTION_SET_RESULT = 'Select the correct options for this prediction\n\n*{}*\n{}'
PREDICTION_SET_RESULT_CONFIRMATION_REQUEST = 'Are you sure you want to set the result of this prediction?' \
                                             '\nThe wagers will be distributed accordingly to the winners and.' \
                                             '\nThis action cannot be undone' \
                                             '\n\nCorrect options:' \
                                             '{}'
PREDICTION_SET_RESULT_SUCCESS = 'Prediction result set successfully'
PREDICTION_SET_RESULT_CONFIRMATION_REQUEST_NO_CORRECT_OPTION = 'No correct option set, wagers will be refunded.'

# Crew - Private
CREW_MAINTAIN_LEADERBOARD_REQUIRED_APPEARANCES_SUFFIX = \
    f'{Env.CREW_MAINTAIN_MIN_LATEST_LEADERBOARD_APPEARANCE.get_int() - 1} global leaderboards'
CREW_USER_NOT_IN_CREW = f'You are not in a Crew. Head over a Chat Group to the to join' \
                        f' one or create your own.' \
                        f'\n\nCreating a Crew will cost ฿{Env.CREW_CREATE_PRICE.get_belly()}.' \
                        f'\n\nIf you create a Crew, you must appear at least once every ' \
                        f'{CREW_MAINTAIN_LEADERBOARD_REQUIRED_APPEARANCES_SUFFIX} or else your Crew will be disbanded.'
CREW_OVERVIEW = '*{}*' \
                '\n\nTreasure Chest: ฿{}' \
                '\n{}'
CREW_OVERVIEW_MEMBER = '\n{}. {}'
CREW_OVERVIEW_MEMBER_ROLE = f'{CREW_OVERVIEW_MEMBER} ' + '\\({}\\)'
CREW_USER_ALREADY_IN_CREW = 'You are already in a Crew'
CREW_CREATE_USER_NOT_ENOUGH_BOUNTY = f"Insufficient bounty, forming a Crew costs " \
                                     f"฿{Env.CREW_CREATE_PRICE.get_belly()}"
CREW_CANNOT_CREATE_CREW = 'You can create a Crew in {}'
CREW_CREATE_REQUEST_NAME = 'Send the name of your Crew'
CREW_CREATE_NAME_ALREADY_EXISTS = 'A Crew with this name already exists'
CREW_CREATE_NAME_TOO_LONG = f'Crew name must be exceed {Env.CREW_NAME_MAX_LENGTH.get_int()} characters'
CREW_CREATE_SUCCESS = 'You are now Captain of the *{}*.' + \
                      f'\n\nHead over to a Chat Group to start recruiting members!'
CREW_NAME_EDIT_SUCCESS = 'Crew name updated successfully'

# Crew - Join request
CREW_JOIN_REQUEST_CREW_FULL = 'The Crew is full'
CREW_NOT_FOUND = 'Crew not found'
CREW_JOIN_REQUEST_CAPTION = 'My name is {}!!! I do not know who you are, but I ask you!!' \
                            '\nLet me ride on your ship!!' \
                            '\n\n_Only the [Captain](tg://user?id={}) can accept or reject this request_'
CREW_JOIN_REQUEST_ACCEPTED = "{} is now a member of {}!"
CREW_JOIN_REQUEST_REJECTED = "[Your](tg://user?id={}) request to join the *{}* has been rejected, but don't give up!!"
CREW_JOIN_REQUEST_CREW_CANNOT_ACCEPT_USER = 'The User cannot join this Crew'
CREW_JOIN_REQUEST_USER_CANNOT_JOIN_CREW = 'You cannot join this Crew'
CREW_USER_CANNOT_JOIN_CREW_UNTIL_RESET = 'You cannot join a Crew until the next weekly leaderboard in {}'
CREW_JOIN_REQUEST_CREW_CANNOT_ACCEPT_NEW_MEMBERS_UNTIL_NEXT_RESET = 'The Crew cannot accept new members until the ' \
                                                                    'next weekly leaderboard in {}'

# Crew - Invite request
CREW_INVITE_REQUEST_CAPTION = "I'm {} and this meeting must be fate, {}! " \
                              "\nWhat do you say to turning the world upside down with me?"
CREW_INVITE_REQUEST_ACCEPTED = "{} is now a member of {}!"
CREW_INVITE_REQUEST_REJECTED = "Invitation to join the *{}* has been rejected by {}"

STEP_REQUIRES_TEXT = 'Please send a valid text'
ITEM_NOT_FOUND = 'Item not found. If you think this is a mistake, please contact an Admin'
INLINE_QUERY_ITEM_NOT_FOUND_TITLE = 'Item not found'
INLINE_QUERY_ITEM_NOT_FOUND_DESCRIPTION = 'Restart the Bot to retrieve a valid url'
INLINE_QUERY_ITEM_NOT_FOUND_MESSAGE = 'Error'

# Crew - Leave
CREW_LEAVE_CONFIRMATION = 'Are you sure you want to leave the Crew?' \
                          '\nYou will not be able to join another Crew until the next weekly leaderboard in {}'
CREW_LEAVE_CONFIRMATION_LOCATION_DOWNGRADE = ' and your location will be downgraded to {} \\(current location: {}\\)'
CREW_LEAVE_SUCCESS = 'You have left the Crew'

# Crew - Disband
CREW_DISBAND_CONFIRMATION = 'Are you sure you want to disband the Crew?\n' \
                            'You will not be able to create another Crew until the next bounty reset in {}'
CREW_DISBAND_SUCCESS = 'You have disbanded the Crew'

# Crew - Member
CREW_MEMBER = '*{}*' \
              '\n\n*Bounty*: ฿{}' \
              '\n*Join Date*: {} \\({}°\\)' \
              '\n\nChest contribution: ฿{} \\({}°\\)' \
              '\nCrew MVP Bonus: {}'

# Crew - Remove member
CREW_NOT_SAME = 'You are not in the same Crew'
CREW_REMOVE_MEMBER_CONFIRMATION = 'Are you sure you want to remove {} from the Crew?' \
                                  '\nYou will not be able accept new members until the next weekly leaderboard in {}'
CREW_REMOVE_MEMBER_SUCCESS = '{} has been removed from the Crew'

# Bounty Gift
BOUNTY_GIFT_NO_AMOUNT = 'You need to specify the amount of belly you want to gift' \
                        f'\n\nExample: {Command.GRP_BOUNTY_GIFT.get_formatted()} 10.000.000'
BOUNTY_GIFT_REQUEST = 'Are you sure you want to gift ฿*{}* to {}?' \
                      '\n\nTax: ฿{} \\({}%\\)' \
                      '\nTotal: ฿*{}*'
BOUNTY_GIFT_CONFIRMED = 'You have gifted ฿*{}* to {}' \
                        '\n\nTax: ฿{} \\({}%\\)' \
                        '\nTotal: ฿*{}*'
BOUNTY_GIFT_CANCELLED = 'Gift cancelled'
BOUNTY_GIFT_NOT_ENOUGH_BOUNTY = 'You do not have enough belly to gift' \
                                '\n\nAvailable belly: ฿{}' \
                                '\nGift amount: ฿*{}*' \
                                '\nTax: ฿{} \\({}%\\)' \
                                '\nTotal: ฿*{}*' \
                                '\n\nYou can gift up to ฿`{}`'

# Bounty Loan
BOUNTY_LOAN_INVALID_COMMAND = 'You need to specify the amount to loan, the amount to repay and the duration' \
                              f'\n\nExample: {Command.GRP_BOUNTY_LOAN.get_formatted()} 100mil 150mil 1day'
BOUNTY_LOAN_LOANER = '\nLoaner: {}'
BOUNTY_LOAN_BORROWER = '\nBorrower: {}'
BOUNTY_LOAN_AMOUNT = '\nAmount: ฿*{}*'
BOUNTY_LOAN_REPAY_AMOUNT = '\nRepay amount: ฿*{}*'
BOUNTY_LOAN_AMOUNT_REPAID = '\nAmount paid: ฿*{}*'
BOUNTY_LOAN_AMOUNT_REMAINING = '\nAmount remaining: ฿*{}*'
BOUNTY_LOAN_AMOUNT_REMAINING_MONOSPACE = '\nAmount remaining: ฿`{}`'
BOUNTY_LOAN_DATE = '\nDate: *{}*'
BOUNTY_LOAN_DURATION = '\nDuration: *{}*'
BOUNTY_LOAN_DEADLINE_DATE = '\nDeadline: *{}*'
BOUNTY_LOAN_TAX = '\nTax: ฿{} \\({}%\\)'
BOUNTY_LOAN_TOTAL = '\nTotal: ฿*{}*'
BOUNTY_LOAN_STATUS = '\n\nStatus: *{}*'
BOUNTY_LOAN_CANCELLED = 'Loan cancelled'
BOUNTY_LOAN_NOT_ENOUGH_BOUNTY = 'You do not have enough belly to loan' \
                                '\n\nAvailable belly: ฿{}' \
                                '\nLoan amount: ฿*{}*' \
                                '\nTax: ฿{} \\({}%\\)' \
                                '\nTotal: ฿*{}*' \
                                '\n\nYou can loan up to ฿`{}`'
BOUNTY_LOAN_STATUS_AWAITING_LOANER_CONFIRMATION = 'Awaiting loaner confirmation'
BOUNTY_LOAN_STATUS_AWAITING_BORROWER_CONFIRMATION = 'Awaiting borrower confirmation'
BOUNTY_LOAN_STATUS_ACTIVE = 'Active'
BOUNTY_LOAN_STATUS_REPAID = 'Re-paid'
BOUNTY_LOAN_STATUS_EXPIRED = 'Expired'
BOUNTY_LOAN_STATUS_FORGIVEN = 'Forgiven'
BOUNTY_LOAN_EXPIRED_ACTION_WARNING_PREFIX = '\n\n_In case the loan is not repaid in time, '
BOUNTY_LOAN_EXPIRED_ACTION_PREFIX = '\n\n_Since the loan was not repaid in time, '
BOUNTY_LOAN_EXPIRED_ACTION_LOANER = '{}% of all new gained bounty by {} will be transferred to you until the loan ' \
                                    'is repaid_'
BOUNTY_LOAN_EXPIRED_ACTION_BORROWER = '{}% of all new gained bounty will be transferred to {} until the loan is repaid_'
BOUNTY_LOAN_EXPIRED_ACTION_LOANER_AND_BORROWER = '{}% of all new gained bounty by {} will be transferred to {} ' \
                                                 'until the loan is repaid_'
BOUNTY_LOAN_REQUEST = '*New Loan*' \
                      '\n' + BOUNTY_LOAN_LOANER \
                      + BOUNTY_LOAN_BORROWER \
                      + BOUNTY_LOAN_AMOUNT \
                      + BOUNTY_LOAN_REPAY_AMOUNT \
                      + BOUNTY_LOAN_DURATION \
                      + BOUNTY_LOAN_TAX \
                      + BOUNTY_LOAN_TOTAL \
                      + BOUNTY_LOAN_STATUS \
                      + BOUNTY_LOAN_EXPIRED_ACTION_WARNING_PREFIX \
                      + BOUNTY_LOAN_EXPIRED_ACTION_LOANER_AND_BORROWER \
                      + '\n\n_To manage or pay this loan, go to Private Chat -> /start -> Loan_'
# Bounty loan - Private Chat
BOUNTY_LOAN_ITEM_TEXT = '{} ฿{} {} {}'
BOUNTY_LOAN_ITEM_TEXT_FILL_IN = 'Loan'
BOUNTY_LOAN_ITEM_NOT_ACTIVE = 'This loan is no longer active'
BOUNTY_LOAN_ITEM_PAY_REQUEST = BOUNTY_LOAN_REPAY_AMOUNT.strip() \
                               + BOUNTY_LOAN_AMOUNT_REPAID \
                               + BOUNTY_LOAN_AMOUNT_REMAINING_MONOSPACE \
                               + '\n\n_Please send the amount you want to pay ' \
                                 '\\(send \\* to repay the maximum allowed by your bounty\\)_'
BOUNTY_LOAN_ITEM_PAY_CONFIRMATION_REQUEST = 'Are you sure you want to pay ฿*{}* for this loan?'
BOUNTY_LOAN_ITEM_PAY_SUCCESS = 'You have successfully paid ฿{} for this loan'
BOUNTY_LOAN_ITEM_FORGIVE_CONFIRMATION_REQUEST = BOUNTY_LOAN_REPAY_AMOUNT.strip() \
                                                + BOUNTY_LOAN_AMOUNT_REPAID \
                                                + BOUNTY_LOAN_AMOUNT_REMAINING_MONOSPACE \
                                                + '\n\nAre you sure you want to forgive this loan?' \
                                                  '\nYou will not be able to collect the remaining amount'
BOUNTY_LOAN_ITEM_FORGIVE_SUCCESS = 'You have forgiven this loan'

# Notification - Categories
NOTIFICATION_CATEGORY_BOUNTY_GIFT = 'Bounty Gift'
NOTIFICATION_CATEGORY_BOUNTY_LOAN = 'Bounty Loan'
NOTIFICATION_CATEGORY_CREW = 'Crew'
NOTIFICATION_CATEGORY_DELETED_MESSAGE = 'Deleted Message'
NOTIFICATION_CATEGORY_GAME = 'Game'
NOTIFICATION_CATEGORY_IMPEL_DOWN = 'Impel Down'
NOTIFICATION_CATEGORY_LOCATION = 'Location'
NOTIFICATION_CATEGORY_PREDICTION = 'Prediction'
NOTIFICATION_CATEGORY_DEVIL_FRUIT = 'Devil Fruit'

# Notification - Crew Leave
CREW_LEAVE_NOTIFICATION = '{} has left the Crew'
CREW_LEAVE_NOTIFICATION_DESCRIPTION = 'If to be notified when a member leaves the Crew. ' \
                                      '\nApplicable only if you are the Captain of the Crew.'
CREW_LEAVE_NOTIFICATION_KEY = 'Crew leave'
# Notification - Crew Member removed
CREW_MEMBER_REMOVE_NOTIFICATION = 'You have been removed from the Crew'
CREW_MEMBER_REMOVE_NOTIFICATION_DESCRIPTION = 'If to be notified when you are removed from the Crew.'
CREW_MEMBER_REMOVE_NOTIFICATION_KEY = 'Crew member removed'
# Notification - Crew Disband
CREW_DISBAND_NOTIFICATION = 'Your Crew has been disbanded'
CREW_DISBAND_NOTIFICATION_DESCRIPTION = 'If to be notified when your Crew is disbanded.'
CREW_DISBAND_NOTIFICATION_KEY = 'Crew disband'
# Notification - Crew disband warning
CREW_DISBAND_WARNING_NOTIFICATION = f'You have not appeared in the last ' \
                                    f'{CREW_MAINTAIN_LEADERBOARD_REQUIRED_APPEARANCES_SUFFIX}.' \
                                    '\nIf you do not appear in the next leaderboard, your Crew will be disbanded.'
CREW_DISBAND_WARNING_NOTIFICATION_DESCRIPTION = \
    'If to be notified a week before your Crew is disbanded due to not appearing in the global leaderboard for ' \
    f'{Env.CREW_MAINTAIN_MIN_LATEST_LEADERBOARD_APPEARANCE.get_int()} consecutive leaderboards.' \
    f'\nApplicable only if you are the Captain of the Crew.'
CREW_DISBAND_WARNING_NOTIFICATION_KEY = 'Crew disband warning'
# Notification - Game turn
GAME_TURN_NOTIFICATION = "It's your turn to play in {} against {}." \
                         f'\n\n[{Emoji.RIGHT_ARROW}Click here to view the game{Emoji.LEFT_ARROW}]' + '({})'
GAME_TURN_NOTIFICATION_DESCRIPTION = 'If to be notified when it is your turn to play in a game if no action is taken ' \
                                     f'for {Env.GAME_TURN_NOTIFICATION_TIME.get_int()} seconds'
GAME_TURN_NOTIFICATION_KEY = 'Game turn'
# Notification - Location
LOCATION_UPDATE_NOTIFICATION = '{}Congratulations {}!' \
                               '\nYou are now {} {}' \
                               '\n\n{}'
LOCATION_NEXT_LEVEL_REQUIREMENT = '_Requirement for next location: ฿*{}*_'
LOCATION_CURRENT_LEVEL_MAX = '_You have reached the maximum location_'
LOCATION_UPDATE_NOTIFICATION_DESCRIPTION = 'If to be notified when you level up to a new location.'
LOCATION_UPDATE_NOTIFICATION_KEY = 'Location update'
# Notification - Impel Down restriction placed
IMPEL_DOWN_RESTRICTION_PLACED_NOTIFICATION = f'{Emoji.DISCIPLINARY_ACTION}*DISCIPLINARY ACTION*' \
                                             f'{Emoji.DISCIPLINARY_ACTION}' \
                                             '\n\n*Reason*: {}' \
                                             '\n\n*Restrictions*:{}{}'
IMPEL_DOWN_RESTRICTION_PLACED_NOTIFICATION_BOUNTY_HALVED = '\n- Bounty halved'
IMPEL_DOWN_RESTRICTION_PLACED_NOTIFICATION_BOUNTY_ERASED = '\n- Bounty erased'
IMPEL_DOWN_RESTRICTION_PLACED_NOTIFICATION_WITH_DURATION = "\n- You can't acquire any new bounty" \
                                                           "\n- You can't appear in the leaderboard" \
                                                           "\n- You can't challenge other users or play games" \
                                                           "\n- You can't bet in polls"
IMPEL_DOWN_RESTRICTION_PLACED_NOTIFICATION_DURATION = '\n\n*Duration*: {}'
IMPEL_DOWN_RESTRICTION_PLACED_NOTIFICATION_DURATION_PERMANENT = 'Permanent'
IMPEL_DOWN_RESTRICTION_PLACED_NOTIFICATION_DESCRIPTION = 'If to be notified when you are restricted'
IMPEL_DOWN_RESTRICTION_PLACED_NOTIFICATION_KEY = 'Restriction placed'
# Notification - Impel Down restriction removed
IMPEL_DOWN_RESTRICTION_REMOVED_NOTIFICATION = 'All restrictions have been removed'
IMPEL_DOWN_RESTRICTION_REMOVED_NOTIFICATION_DESCRIPTION = 'If to be notified when all restrictions are removed'
IMPEL_DOWN_RESTRICTION_REMOVED_NOTIFICATION_KEY = 'Restriction removed'
# Notification - Prediction result
PREDICTION_RESULT_NOTIFICATION = 'You *{}* ฿{} in the prediction "*{}*"{}{}{}'
PREDICTION_RESULT_NOTIFICATION_WAGER_REFUNDED = '_\n\n\\(Your wager was refunded\\)_'
PREDICTION_RESULT_NOTIFICATION_WAGER_REFUNDED_PARTIAL = '_\n\n\\(You have been refunded ฿{}\\)_'
PREDICTION_RESULT_NOTIFICATION_WAGER_REFUNDED_NO_CORRECT_OPTIONS = '_\n\n\\(Your wager was refunded because there' \
                                                                   ' were no correct options\\)_'
PREDICTION_RESULT_NOTIFICATION_OPTION = '\n{}{}'
PREDICTION_RESULT_NOTIFICATION_OPTION_NO_EMOJI = '\n- {}'
PREDICTION_RESULT_NOTIFICATION_YOUR_OPTION = '\n\n*Your option*: {}'
PREDICTION_RESULT_NOTIFICATION_YOUR_OPTIONS = '\n\n*Your options*: {}'
PREDICTION_RESULT_NOTIFICATION_CORRECT_OPTION = '\n\n*Correct option*: {}'
PREDICTION_RESULT_NOTIFICATION_CORRECT_OPTIONS = '\n\n*Correct options*: {}'
PREDICTION_RESULT_NOTIFICATION_DESCRIPTION = 'If to be notified of the outcome of a prediction you participated in'
PREDICTION_RESULT_NOTIFICATION_KEY = 'Prediction result'
# Notification - Prediction bet invalid
PREDICTION_BET_INVALID_BET_HAS = 'bet has'
PREDICTION_BET_INVALID_BETS_HAVE = 'bets have'
PREDICTION_BET_INVALID_NOTIFICATION = 'The following {} been removed from the prediction "*{}*"' + \
                                      ' because {} placed after the cut off time \\({}\\):\n{}' + \
                                      '\n\n_You have been refunded ฿{}_'
PREDICTION_BET_INVALID_NOTIFICATION_OPTION = '\n- {} \\({}\\)'
PREDICTION_BET_INVALID_NOTIFICATION_DESCRIPTION = 'If to be notified when a bet you placed is removed from a ' \
                                                  'because it was placed after the cut off time'
PREDICTION_BET_INVALID_NOTIFICATION_KEY = 'Prediction bet removed'
# Notification - Deleted message because of arrest
ABOVE_MESSAGE_DELETED_FROM_CHAT_GROUP = f'The above message was deleted from the Group Chat because you '
DELETED_MESSAGE_ARREST_NOTIFICATION = f'{ABOVE_MESSAGE_DELETED_FROM_CHAT_GROUP} are arrested'
DELETED_MESSAGE_ARREST_NOTIFICATION_DESCRIPTION = 'If to be notified when a message you sent in the ' \
                                                  'Group Chat was deleted because you are arrested'
DELETED_MESSAGE_ARREST_NOTIFICATION_KEY = 'Deleted message arrest'
# Notification - Deleted message because of user is muted
DELETED_MESSAGE_MUTE_NOTIFICATION = f'{ABOVE_MESSAGE_DELETED_FROM_CHAT_GROUP} are muted'
DELETED_MESSAGE_MUTE_NOTIFICATION_DESCRIPTION = 'If to be notified when a message you sent in the ' \
                                                'Group Chat was deleted because you are muted'
DELETED_MESSAGE_MUTE_NOTIFICATION_KEY = 'Deleted message mute'
# Notification - Deleted message because of user has not reached the required location
DELETED_MESSAGE_LOCATION_NOTIFICATION = f'{ABOVE_MESSAGE_DELETED_FROM_CHAT_GROUP} have not reached the required ' \
                                        'location to send this type of message.' \
                                        '\n\n*Your location*: {}' \
                                        '\n*Required location*: {}'
DELETED_MESSAGE_LOCATION_NOTIFICATION_DESCRIPTION = 'If to be notified when a message you sent in the ' \
                                                    'Group Chat was deleted because you have not reached ' \
                                                    'the required location to send that type of message'
DELETED_MESSAGE_LOCATION_NOTIFICATION_KEY = 'Deleted message location'
# Notification - Bounty Gift
BOUNTY_GIFT_RECEIVED_NOTIFICATION = 'You have been gifted ฿{} by {}'
BOUNTY_GIFT_RECEIVED_NOTIFICATION_DESCRIPTION = 'If to be notified when you are gifted bounties'
BOUNTY_GIFT_RECEIVED_NOTIFICATION_KEY = 'Bounty gift'
# Notification - Devil Fruit Awarded
DEVIL_FRUIT_EAT_OR_SELL = f"\n\nYou can eat it or sell it with the {Command.GRP_DEVIL_FRUIT_SELL.get_formatted()} " \
                          f"command in a group"
DEVIL_FRUIT_AWARDED_NOTIFICATION = 'You have been awarded the following Devil Fruit:' \
                                   '\n\n*{}*' \
                                   '\nReason: {}' \
                                   + DEVIL_FRUIT_EAT_OR_SELL
DEVIL_FRUIT_AWARDED_NOTIFICATION_DESCRIPTION = 'If to be notified when you are awarded a Devil Fruit'
DEVIL_FRUIT_AWARDED_NOTIFICATION_KEY = 'Devil Fruit award'
# Notification - Devil Fruit Expired
DEVIL_FRUIT_EXPIRED_NOTIFICATION = 'Your Devil Fruit *{}* has expired and has been revoked'
DEVIL_FRUIT_EXPIRED_NOTIFICATION_DESCRIPTION = 'If to be notified when your Devil Fruit expires'
DEVIL_FRUIT_EXPIRED_NOTIFICATION_KEY = 'Devil Fruit expired'
# Notification - Devil Fruit revoke
DEVIL_FRUIT_REVOKE_NOTIFICATION = 'Your Devil Fruit *{}* has been revoked'
DEVIL_FRUIT_REVOKE_NOTIFICATION_DESCRIPTION = 'If to be notified when your Devil Fruit is revoked'
DEVIL_FRUIT_REVOKE_NOTIFICATION_KEY = 'Devil Fruit revoked'
# Notification - Devil Fruit revoke warning
DEVIL_FRUIT_REVOKE_WARNING_NOTIFICATION = f'You have not appeared in the last ' \
                                          f'{Env.DEVIL_FRUIT_MAINTAIN_MIN_LATEST_LEADERBOARD_APPEARANCE.get_int() - 1}' \
                                          f' leaderboards.' \
                                          '\nIf you do not appear in the next leaderboard, your Devil Fruit *{}* ' \
                                          'will be revoked.'
DEVIL_FRUIT_REVOKE_WARNING_NOTIFICATION_DESCRIPTION = \
    'If to be notified a week before the Devil Fruit you ate is revoked due to not appearing in the leaderboard for ' \
    f'{Env.DEVIL_FRUIT_MAINTAIN_MIN_LATEST_LEADERBOARD_APPEARANCE.get()} consecutive leaderboards'
DEVIL_FRUIT_REVOKE_WARNING_NOTIFICATION_KEY = 'Devil Fruit revoke warning'
# Notification - Bounty Loan
BOUNTY_LOAN_NOTIFICATION_GO_TO_ITEM_BUTTON_TEXT = 'Go to loan'
# Notification - Bounty Loan Payment
BOUNTY_LOAN_PAYMENT_NOTIFICATION = 'You have received a payment of ฿{} from {} for your loan'
BOUNTY_LOAN_PAYMENT_NOTIFICATION_DESCRIPTION = 'If to be notified when you receive a payment for your loan'
BOUNTY_LOAN_PAYMENT_NOTIFICATION_KEY = 'Bounty loan payment'
# Notification - Bounty Loan Forgiven
BOUNTY_LOAN_FORGIVEN_NOTIFICATION = 'Your loan of ฿{} from {} has been forgiven'
BOUNTY_LOAN_FORGIVEN_NOTIFICATION_DESCRIPTION = 'If to be notified when your loan is forgiven'
BOUNTY_LOAN_FORGIVEN_NOTIFICATION_KEY = 'Bounty loan forgiven'
# Notification - Bounty Loan Expired
BOUNTY_LOAN_EXPIRED_NOTIFICATION = 'Your loan of ฿{} from {} has expired.' \
                                   + BOUNTY_LOAN_EXPIRED_ACTION_PREFIX \
                                   + BOUNTY_LOAN_EXPIRED_ACTION_BORROWER
BOUNTY_LOAN_EXPIRED_NOTIFICATION_DESCRIPTION = 'If to be notified when your loan expires'
BOUNTY_LOAN_EXPIRED_NOTIFICATION_KEY = 'Bounty loan expired'

# List
LIST_OVERVIEW = 'Select' + ' {} *{}* from the list below\n{}'  # In the chunk to avoid IDE recognizing it as SQL
LIST_ITEM_TEXT = '\n*{}*. {}'
LIST_FOOTER = '\n\n_Showing {}-{} of {} items_'
NAVIGATION_LIMIT_REACHED = 'Limit reached'

# Logs
LOG_ITEM_DETAIL_OUTCOME_TEXT = '{}You *{}*'
LOG_ITEM_DETAIL_OUTCOME_BELLY_TEXT = '{}You *{}* ฿{}'
LOG_ITEM_DETAIL_STATUS_TEXT = '*Status*: {}'
LOG_ITEM_DETAIL_GO_TO_MESSAGE = (f'\n\n{Emoji.RIGHT_ARROW}[Go to message](' + '{}' + f'){Emoji.LEFT_ARROW}' +
                                 '\n_\\(The message may no longer be available\\)_')
LOG_ITEM_DETAIL_NO_PERMISSION = 'You are not authorized to view this item'
LOG_STATS_TEXT = '*{} Statistics*\n\n{}'
LOG_STATS_NOT_ENOUGH_DATA = 'Not enough data to generate statistics for this log'
# Logs - Fight
FIGHT_LOG_KEY = 'Fights'
FIGHT_LOG_ITEM_DETAIL_TEXT_FILL_IN = 'Fight'
FIGHT_LOG_ITEM_TEXT = '{} vs {} \\(฿{}\\)'
FIGHT_LOG_ITEM_DETAIL_TEXT = '*{}*: {}' \
                             '\n*Date*: {}' \
                             '\n*Win probability*: {}%' \
                             '\n\n{}' \
                             f'{LOG_ITEM_DETAIL_GO_TO_MESSAGE}'
FIGHT_LOG_STATS_TEXT = '*Total fights*: {}' \
                       '\n*Wins*: {} \\({}%\\)' \
                       '\n*Losses*: {} \\({}%\\)' \
                       '\n*Belly won*: ฿{}' \
                       '\n*Belly lost*: ฿{}' \
                       '\n*Max belly won*: [฿{} \\({}\\)]({})' \
                       '\n*Max belly lost*: [฿{} \\({}\\)]({})' \
                       '\n*Most fought user*: {} \\({}x\\)'

# Logs - DocQ
DOC_Q_GAME_LOG_KEY = 'Doc Q'
DOC_Q_GAME_LOG_ITEM_DETAIL_TEXT_FILL_IN = 'Doc Q Game'
DOC_Q_GAME_LOG_ITEM_TEXT = '{} ฿{}'
DOC_Q_GAME_LOG_ITEM_DETAIL_TEXT = '*Date*: {}' \
                                  '\n*Correct apple*: {}°' \
                                  '\n\n{}' \
                                  f'{LOG_ITEM_DETAIL_GO_TO_MESSAGE}'
DOC_Q_GAME_LOG_STATS_TEXT = '*Total summons*: {}' \
                            '\n*Wins*: {} \\({}%\\)' \
                            '\n*Losses*: {} \\({}%\\)' \
                            '\n*Belly won*: ฿{}' \
                            '\n*Belly lost*: ฿{}' \
                            '\n*Max belly won*: [฿{}]({})' \
                            '\n*Max belly lost*: [฿{}]({})' \
                            '\n' \
 \
    # Logs - Game
GAME_LOG_KEY = 'Challenges'
GAME_LOG_ITEM_DETAIL_TEXT_FILL_IN = 'Challenge'
GAME_LOG_ITEM_TEXT = '{} vs {} \\(฿{}\\)'
GAME_LOG_ITEM_DETAIL_TEXT = '*{}*: {}' \
                            '\n*Game*: {}' \
                            '\n*Date*: {}' \
                            '\n*Wager*: ฿{}' \
                            '\n\n{}' \
                            f'{LOG_ITEM_DETAIL_GO_TO_MESSAGE}'
GAME_LOG_STATS_TEXT = '*Total challenges*: {}' \
                      '\n*Wins*: {} \\({}%\\)' \
                      '\n*Losses*: {} \\({}%\\)' \
                      '\n*Draws*: {} \\({}%\\)' \
                      '\n*Belly won*: ฿{}' \
                      '\n*Belly lost*: ฿{}' \
                      '\n*Max belly won*: [฿{} \\({}\\)]({})' \
                      '\n*Max belly lost*: [฿{} \\({}\\)]({})' \
                      '\n*Most challenged user*: {} \\({}x\\)' \
                      '\n*Most played game*: {} \\({}x\\)'

# Logs - Bounty Gift
BOUNTY_GIFT_LOG_KEY = 'Bounty Gifts'
BOUNTY_GIFT_LOG_ITEM_DETAIL_TEXT_FILL_IN = 'Bounty Gift'
BOUNTY_GIFT_LOG_ITEM_TEXT = '{} ฿{} {} {}'
BOUNTY_GIFT_LOG_ITEM_DETAIL_TAX_TEXT = '\n*Tax*: ฿{} \\({}%\\)' \
                                       '\n*Total*: ฿{}'
BOUNTY_GIFT_LOG_ITEM_DETAIL_TEXT = '*{}*: {}' \
                                   '\n*Date*: {}' \
                                   '\n*Amount*: ฿{}{}' \
                                   f'{LOG_ITEM_DETAIL_GO_TO_MESSAGE}'
BOUNTY_GIFT_LOG_STATS_TEXT = '*Total gifts*: {}' \
                             '\n*Total given*: ฿{}' \
                             '\n*Total received*: ฿{}' \
                             '\n*Highest given*: [฿{} \\({}\\)]({})' \
                             '\n*Highest received*: [฿{} \\({}\\)]({})' \
                             '\n*Top receiver*: {} \\(฿{}\\)' \
                             '\n*Top giver*: {} \\(฿{}\\)'

# Logs - Legendary Pirate
LEGENDARY_PIRATE_LOG_KEY = 'Legendary Pirates'
LEGENDARY_PIRATE_LOG_ITEM_DETAIL_TEXT_FILL_IN = 'Legendary Pirate'
LEGENDARY_PIRATE_LOG_ITEM_TEXT = '{}'
LEGENDARY_PIRATE_LOG_ITEM_DETAIL_TEXT = '*{}*' \
                                        '\nEpithet: {}' \
                                        '\n\n*Reason*: {}'

# Logs - New World Pirate
NEW_WORLD_PIRATE_LOG_KEY = 'New World Pirates'
NEW_WORLD_PIRATE_LOG_ITEM_DETAIL_TEXT_FILL_IN = 'New World Pirate'
NEW_WORLD_PIRATE_LOG_ITEM_TEXT = '{} \\(฿{}\\)'
NEW_WORLD_PIRATE_LOG_ITEM_DETAIL_CREW_TEXT = '\n*Crew*: {}'
NEW_WORLD_PIRATE_LOG_ITEM_DETAIL_TEXT = '*{}*' \
                                        '\n\n*Bounty*: ฿{}' \
                                        '\n*Location*: {}{}'

# Logs - Leaderboard Rank
LEADERBOARD_RANK_LOG_KEY = 'Global Leaderboard Ranks'
LEADERBOARD_RANK_LOG_ITEM_DETAIL_TEXT_FILL_IN = 'Global Leaderboard Rank'
LEADERBOARD_RANK_LOG_ITEM_TEXT = 'Week {} of {} - {}'
LEADERBOARD_RANK_LOG_ITEM_DETAIL_TEXT = '*Week {} of {}*' \
                                        '\n\n*Position*: {}°' \
                                        '\n*Rank*: {}' \
                                        '\n*Bounty*: ฿{}'
LEADERBOARD_RANK_LOG_STATS_TEXT = '*Total appearances*: {}' \
                                  '\n*Appearances as Pirate King*: {} \\({}%\\)' \
                                  '\n*Appearances as Emperor*: {} \\({}%\\)' \
                                  '\n*Appearances as First Mate*: {} \\({}%\\)' \
                                  '\n*Appearances as Supernova*: {} \\({}%\\)' \
                                  '\n*Max rank*: [{} \\({}°\\)]({})' \
                                  '\n*Max bounty*: [฿{} \\({}°\\)]({})'

# Logs - Income tax event
INCOME_TAX_EVENT_LOG_KEY = 'Tax Breakdown'
INCOME_TAX_EVENT_LOG_ITEM_DETAIL_TEXT_FILL_IN = 'Income Tax Breakdown'
INCOME_TAX_EVENT_LOG_ITEM_TEXT = '{} \\(฿{}\\)'
INCOME_TAX_EVENT_LOG_ITEM_DETAIL_TEXT = '*Event*: [{}]({})' \
                                        '\n*Date*: {}' \
                                        '\n*Income*: ฿{}' \
                                        '\n*Net gain*: ' \
                                        + Emoji.LOG_POSITIVE + '฿{}' \
                                                               '\n*Total tax*: ' \
                                        + Emoji.LOG_NEGATIVE + '฿{} \\({}%\\)' \
                                                               '{}{}' \
                                                               '\n\n\n*Breakdown*' \
                                                               '{}'
INCOME_TAX_EVENT_LOG_ITEM_DETAIL_TEXT_DEDUCTION = '\n\n*Deductions*'
INCOME_TAX_EVENT_LOG_ITEM_DETAIL_TEXT_DEDUCTION_ITEM = '\n{}: {}%'
INCOME_TAX_EVENT_LOG_ITEM_DETAIL_TEXT_CONTRIBUTION = '\n\n*Contributions* \\(from tax\\)'
INCOME_TAX_EVENT_LOG_ITEM_DETAIL_TEXT_CONTRIBUTION_ITEM = '\n{}: ฿{} \\({}%\\)'

INCOME_TAX_EVENT_LOG_ITEM_DETAIL_TEXT_BREAKDOWN_ITEM = '\n\nAmount: ฿{}' \
                                                       '\nGain: ฿{}' \
                                                       '\nTax: ฿{} \\({}%\\)'

SILENCE_ACTIVE = 'A soundproof field has been activated, only those who are granted permission can speak'
SILENCE_END = 'The soundproof field has been cancelled, everyone can speak again'
SPEAK = '{} has been granted permission to speak'

# Devil Fruit
DEVIL_FRUIT_ABILITY_TEXT = '\n\n*Abilities*'
DEVIL_FRUIT_ABILITY_TEXT_LINE = '\n{}{}: \\({}{}%\\)'
DEVIL_FRUIT_ABILITY_UNKNOWN = '\nUnknown'
# Devil Fruit - Private Chat
DEVIL_FRUIT_ITEM_TEXT = '{}'
DEVIL_FRUIT_ITEM_TEXT_FILL_IN = 'Devil Fruit'
DEVIL_FRUIT_ITEM_DETAIL_TEXT = '*{}*' \
                               '\nCategory: {}' \
                               '{}{}{}'
DEVIL_FRUIT_ITEM_DETAIL_TEXT_EXPIRING_DATE = '\n\nExpiring in: {}'
DEVIL_FRUIT_ITEM_DETAIL_TEXT_SELL_COMMAND = f'\n\nYou can sell this Devil Fruit in the Chat Group with' \
                                            f' {Command.GRP_DEVIL_FRUIT_SELL.get_formatted()} <price> command'
DEVIL_FRUIT_LIST_NO_ITEMS = 'You do not have any Devil Fruits'
DEVIL_FRUIT_NOT_OWNER = 'You do not own this Devil Fruit'
DEVIL_FRUIT_EAT_USER_ALREADY_ATE = 'You have already eaten a Devil Fruit'
DEVIL_FRUIT_EAT_CONFIRMATION_REQUEST = 'Are you sure you want to eat the {}?{}' \
                                       '\n\nYou will not be able to eat another Devil Fruit until you discard it'
DEVIL_FRUIT_EAT_CONFIRMATION_REQUEST_ABILITIES = '\nYou will gain the following abilities:\n{}'
DEVIL_FRUIT_EAT_CONFIRMATION_CONFIRMED = 'You have eaten the {} and gained the following abilities:\n{}'
DEVIL_FRUIT_DISCARD_CONFIRMATION_REQUEST = 'Are you sure you want to discard the {}?' \
                                           "\n\nYou will lose it and can regain it by finding or trading for it again"
DEVIL_FRUIT_DISCARD_CONFIRMATION_CONFIRMED = 'You have discarded the {}'
DEVIL_FRUIT_RELEASE_MESSAGE_INFO = "Congratulations {}, you have found a Devil Fruit!" \
                                   "\n\nName: *{}*" \
                                   "\nCategory: {}" \
                                   "{}" \
                                   + DEVIL_FRUIT_EAT_OR_SELL

DEVIL_FRUIT_SELL_NO_AMOUNT = 'You need to specify the amount of belly you want to sell the Devil Fruit for' \
                             f'\n\nExample: {Command.GRP_DEVIL_FRUIT_SELL.get_formatted()} 10.000.000'
DEVIL_FRUIT_SELL_NO_FRUITS = 'You do not have any Devil Fruits that can be sold ' \
                             '\\(only collected and non-eaten Devil Fruits can be sold\\)'
DEVIL_FRUIT_SELL_SELECT_FRUIT = 'Select the Devil Fruit you want to sell' \
                                '\n\n_Tip: When using this command in response to a user, ' \
                                'only they will have the ability to purchase the Devil Fruit_'
DEVIL_FRUIT_SELL_NO_LONGER_OWN = '{} no longer owns this Devil Fruit'
DEVIL_FRUIT_SELL_NO_LONGER_SELLABLE = 'This Devil Fruit is no longer sellable'
DEVIL_FRUIT_SELL_BUY = '{} has put up the following Devil Fruit for sale:' \
                       '\n\n{}' \
                       '\n\nExpiring in: {}' \
                       '\n\nPrice: ฿{}' \
                       '\nTax: ฿{} \\({}%\\)' \
                       '\nTotal Price: ฿*{}*' \
                       '{}'
DEVIL_FRUIT_SELL_BUY_ONLY_BY_USER_ADDENDUM = '\n\n_Only {} can buy this Devil Fruit_'
DEVIL_FRUIT_SELL_BUY_NOT_ENOUGH_BELLY = 'You do not have enough belly to buy this Devil Fruit'
DEVIL_FRUIT_SELL_BUY_CANNOT_BUY_OWN = 'You cannot buy your own Devil Fruit'
DEVIL_FRUIT_SELL_BUY_SUCCESS = '{} has bought the following Devil Fruit from {}' \
                               '\n\n{}' \
                               '\n\nExpiring in: *{}*' \
                               '\n\nPrice: ฿{}' \
                               '\nTax: ฿{} \\({}%\\)' \
                               '\nTotal Price: ฿*{}*'

# Admin chat error messages
NO_DEVIL_FRUIT_TO_SCHEDULE = 'There are no {} Devil Fruits to schedule for release'

THANKS_FOR_ADDING_TO_GROUP = 'Thanks for adding me to your Group!\n'

INCOME_TAX_EVENT_BOUNTY_LOAN = 'Bounty Loan'
INCOME_TAX_EVENT_DEVIL_FRUIT_SELL = 'Devil Fruit Sell'
INCOME_TAX_EVENT_PREDICTION = 'Prediction'

INCOME_TAX_DEDUCTION_TYPE_ADMIN = 'Admin'
INCOME_TAX_DEDUCTION_TYPE_CREW_ABILITY = 'Crew Ability'
INCOME_TAX_DEDUCTION_TYPE_DEVIL_FRUIT = 'Devil Fruit'

INCOME_TAX_CONTRIBUTION_TYPE_CREW_CHEST = 'Crew Chest'

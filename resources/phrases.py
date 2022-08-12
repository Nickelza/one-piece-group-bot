import src.model.enums.Command as Command
from src.model.enums.Emoji import Emoji

COMMAND_NOT_IN_REPLY_ERROR = 'This command can only be used in a reply to a message'
COMMAND_IN_REPLY_TO_BOT_ERROR = "This command can't be used in reply to a bot"
COMMAND_IN_REPLY_TO_ERROR = "This command can't be used in a reply to your own message"
COMMAND_NOT_ACTIVE_ERROR = "This command is no longer available"
COMMAND_NOT_ACTIVE_WITH_REPLACEMENT_ERROR = COMMAND_NOT_ACTIVE_ERROR + '. ' + 'Please Use {} instead'
COMMAND_FOR_NEW_WORLD_USERS_ERROR = 'This command is only available for users in the New World'
COMMAND_FOR_USERS_AFTER_LOCATION_ERROR = 'This command is only available for users who have reached *{}*'

SHOW_USER_STATUS = 'User: {}' \
                   '\nBounty: ฿*{}*{}' \
                   '\nRank: {}' \
                   '\nLocation: {}'
SHOW_USER_STATUS_PENDING_BOUNTY = '\nPending bounty: ฿*{}*'
SHOW_USER_STATUS_FIGHT_IMMUNITY = '\nFight immunity: {}'
SHOW_USER_STATUS_FIGHT_COOLDOWN = '\nFight cooldown: {}'
SHOW_USER_STATUS_ADD_REPLY = '_Requested by {}_'
NOT_ALLOWED_TO_VIEW_REPLIED_STATUS = 'You can only view the status of those who rank below you.' \
                                     '\n\n{} rank: {}' \
                                     '\n{} rank: {}'
ROOKIE_STATUS_PRIVATE_CHAT_ONLY = 'Rookies can only view their status in Private Chat'
STATUS_PRIVATE_CHAT_KEY = 'View in Private Chat'
BOUNTY_RESET = 'Bounties have been reset'

LEADERBOARD_HEADER = '*Leaderboard* for week *{}* of *{}*\n\nHere are the top {} users with the most bounties:\n'
LEADERBOARD_ROW = '{}°: {}\n{} - ฿*{}*'

SAVE_MEDIA_NOT_IN_REPLY_TO_MEDIA = 'This command can only be used in a reply to a media message'
SAVED_MEDIA_UNKNOWN_TYPE = 'Unknown media type. Available types are: *{}*'
SAVE_MEDIA_INVALID_FORMAT = 'Invalid format.\n\nCommand: ' + Command.ADM_SAVE_MEDIA.get_formatted() + ' <name>'
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

# Keyboard options
KEYBOARD_OPTION_CANCEL = Emoji.CANCEL.value + ' Cancel'
KEYBOARD_OPTION_DELETE = Emoji.CANCEL.value + ' Delete'
KEYBOARD_OPTION_ACCEPT = Emoji.ACCEPT.value + ' Accept'
KEYBOARD_OPTION_REJECT = Emoji.REJECT.value + ' Reject'
KEYBOARD_OPTION_FIGHT = Emoji.FIGHT.value + ' Fight'
KEYBOARD_OPTION_RETREAT = Emoji.RETREAT.value + ' Retreat'
KEYBOARD_OPTION_BACK = Emoji.BACK.value + ' Back'

EXCEPTION_CHAT_ID_NOT_PROVIDED = 'chat_id is None and update.effective_chat.id is None'
EXCEPTION_NO_EDIT_MESSAGE = 'new_message is False but update.callback_query is None'
EXCEPTION_SAVED_MEDIA_UNKNOWN_TYPE = 'Unknown media type: {}'

KEYBOARD_NOT_FOUND = 'Keyboard not found'
KEYBOARD_USE_UNAUTHORIZED = 'You are not authorized to use this keyboard'

LOCATION_LEVEL_UP = '{}Congratulations {}!' \
                    '\nYou are now {} {}' \
                    '\n\n{}'
LOCATION_NEXT_LEVEL_REQUIREMENT = '_Requirement for next location: ฿*{}*_'
LOCATION_CURRENT_LEVEL_MAX = '_You have reached the maximum location_'
LOCATION_CHANGE_REGION_PROPOSAL = '{}{} would you like to move to {}?'
LOCATION_CHANGE_REGION_PROPOSAL_REJECTED = '{}{} You can move to {} later with {} command'
LOCATION_NEW_WORLD_REQUEST_REJECTED_NOT_ENOUGH_BOUNTY = 'You need a bounty of at least ฿*{}* to move to the New World.'
LOCATION_ALREADY_IN_REGION = 'You are already in {}'
LOCATION_CANNOT_CHANGE_REGION = 'You can change region in *{}*'
LOCATION_INVALID_CHANGE_REGION_REQUEST = 'Invalid region'

FIGHT_NOT_FOUND = 'Fight not found'
FIGHT_OPPONENT_NOT_FOUND = 'Opponent not found'
FIGHT_CANNOT_FIGHT_USER = "You can't fight this user"
FIGHT_USER_IN_COOLDOWN = "Fight cooldown active. You can initiate a fight in *{}*"
FIGHT_CONFIRMATION_REQUEST = '{} are you sure you want to fight {}?' \
                             '\nI predict a {}% probability of {}.' + '\n\n' + GAME_WIN_LOSE_STATUS
FIGHT_CONFIRMATION_OUTCOME_VICTORY = 'victory'
FIGHT_CONFIRMATION_OUTCOME_DEFEAT = 'defeat'
FIGHT_WIN = "Just as I foresaw, {} won the fight against {}.\n" \
            "I don't need the cards to tell me that your strength is incredible..." + '\n\n' + GAME_WIN_STATUS
FIGHT_LOSE = "Just as I foresaw, {} lost the fight against {}.\n" \
             "Looks like your luck ran out..." + '\n\n' + GAME_LOSE_STATUS
FIGHT_CONFIRMATION_RETREAT = 'You have successfully retreated'

ENABLED = Emoji.ENABLED.value + ' Enabled'
DISABLED = Emoji.DISABLED.value + ' Disabled'
ENABLE = Emoji.ENABLED.value + ' Enable'
DISABLE = Emoji.DISABLED.value + ' Disable'
CURRENT_SETTING = 'Current setting: {}'

# Private chat
PVT_TXT_START = 'Welcome to @onepiecegroup Bot! From here you can manage your profile.'
PVT_KEY_SETTINGS = Emoji.SETTINGS.value + ' Settings'
PVT_KEY_STATUS = Emoji.STATUS.value + ' Status'
PVT_TXT_SETTINGS = 'Which setting would you like to change?'
PVT_KEY_SETTINGS_LOCATION_UPDATE = 'Location update'
PVT_TXT_SETTINGS_LOCATION_UPDATE = 'Do you want to receive an update when you move to a new location?'

ACTION_INSUFFICIENT_BOUNTY = "Insufficient bounty"
ACTION_WAGER_LESS_THAN_MIN = "The minimum wager is ฿*{}*"
ACTION_INVALID_WAGER_AMOUNT = "Invalid wager amount. Make sure it is a number with only '.' or ',' as decimal separator"

GAME_CANNOT_CHALLENGE_USER = "You can't challenge this user"
GAME_CHOOSE_GAME = 'On which game would you like to challenge {}?'
GAME_NO_WAGER_AMOUNT = 'You need to specify a wager amount.' \
                       f'\n\nExample: {Command.GRP_FIGHT.get_formatted()} 10.000.000'

GAME_NOT_FOUND = 'Game not found'
GAME_REQUEST = '{}, you have been challenged by {} to play {} with a wager of ฿*{}*' \
               '\nWould you like to accept?'
GAME_CANCELED = 'Game cancelled'
GAME_CHALLENGE_REJECTED = '{} has rejected the challenge'
GAME_INVALID = 'Invalid game'
GAME_UNKNOWN_NAME = 'Unknown'

ROCK_PAPER_SCISSORS_GAME_NAME = 'Rock Paper Scissors'

ROCK_PAPER_SCISSORS_CHOICE_ALERT = 'You chose {}'
ROCK_PAPER_SCISSORS_CHOICE_ROCK = Emoji.ROCK.value + ' Rock'
ROCK_PAPER_SCISSORS_CHOICE_PAPER = Emoji.PAPER.value + ' Paper'
ROCK_PAPER_SCISSORS_CHOICE_SCISSORS = Emoji.SCISSORS.value + ' Scissors'
ROCK_PAPER_SCISSORS_CHOICES = '{} chose {} ' \
                              '\n{} chose {}\n\n'

RUSSIAN_ROULETTE_GAME_NAME = 'Russian Roulette'
RUSSIAN_ROULETTE_GAME_CHAMBER_ALREADY_FIRED = 'This chamber has already been fired. Choose another one.'
RUSSIAN_ROULETTE_GAME_BULLET_SHOT = "You've died"
RUSSIAN_ROULETTE_GAME_BULLET_NOT_SHOT = "You've survived another round"

GAME_TEXT = '*{}*' \
            '\n\n{} vs {}' \
            '\n*Wager:* ฿*{}*' \
            '\n\n{}'
GAME_STATUS_AWAITING_CHOICE = 'Status: Awaiting choice'
GAME_STATUS_AWAITING_USER_CHOICE = "Status: Awaiting {}'s choice"
GAME_RESULT_DRAW = 'Result: Draw'
GAME_RESULT_WIN = Emoji.WINNER.value + ' {} won'
GAME_NOT_YOUR_TURN = "It's not your turn"
GAME_TURN = "Status: {}'s turn"
GAME_ENDED = 'This game has ended'
GAME_CANNOT_INITIATE = 'Challenge limit reached, make sure you have canceled any pending challenges.' \
                       '\nYou can initiate another challenge in *{}*, but in the meantime you can ask another user ' \
                       'to challenge you.'
GAME_PENDING_KEY = 'Pending challenge'
GAME_FORCED_END = 'This game has ended due to bounty reset. The wagers has been returned to the participants.'

PREDICTION_NOT_FOUND = 'Prediction not found'
PREDICTION_NOT_IN_NEW_STATUS = 'Prediction not in NEW status'
PREDICTION_NOT_SENT = 'Prediction not sent'
PREDICTION_NOT_IN_SENT_STATUS = 'Prediction not in SENT status'
PREDICTION_NOT_IN_BETS_CLOSED_STATUS = 'Prediction not in BETS\\_CLOSED status'
UNKNOWN_PREDICTION_ACTION = 'Unknown prediction action'
PREDICTION_TEXT = '*{}*' \
                  '\n{}' \
                  '\n\n*Status*: {}' \
                  '{}{}'
PREDICTION_TEXT_OPTION = '\n{}. {} \\(*{}%*\\){}'
PREDICTION_CLOSING_DATE = '\n*Closing date*: {}'
PREDICTION_CUT_OFF_DATE = '\n*Cut off date*: {}'
PREDICTION_WAGERS_REFUNDED = f'\n{Emoji.PREDICTION_FEATURE_ENABLED.value} Wagers refunded'
PREDICTION_MULTIPLE_BETS_ALLOWED = f'\n{Emoji.PREDICTION_FEATURE_ENABLED.value} Multiple bets allowed'
PREDICTION_CAN_WITHDRAW_BETS = f'\n{Emoji.PREDICTION_FEATURE_ENABLED.value} Can withdraw bets'
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
PREDICTION_NOT_FOUND_IN_REPLY = 'Prediction not found in replied message. Make sure you replied to a prediction'
PREDICTION_ALREADY_BET = 'You have already bet on this prediction'
PREDICTION_OPTION_NOT_FOUND = 'Option *{}* not found in prediction'
PREDICTION_BET_SUCCESS = 'Bet placed successfully' + PREDICTION_BET_HOW_TO_VIEW_BET_STATUS
PREDICTION_RESULTS_SET = 'The results of this prediction have been set'
PREDICTION_BET_REMOVE_INVALID_FORMAT = 'Make sure your command is in the following format:' \
                                       f'\n{Command.GRP_PREDICTION_BET_REMOVE.get_formatted()} ]<option number>' \
                                       f'\n\nExample: {Command.GRP_PREDICTION_BET_REMOVE.get_formatted()} 1'
PREDICTION_BET_REMOVE_SUCCESS = 'Bet removed successfully'
PREDICTION_BET_USER_HAS_NOT_BET = 'You have not bet on this prediction'
PREDICTION_BET_REMOVE_ALL_SUCCESS = 'All bets removed successfully for this prediction'
PREDICTION_CLOSED_FOR_BETS_REMOVAL = 'You can no longer withdraw bets from this prediction'
PREDICTION_DOES_NOT_ACCEPT_BETS_WITHDRAWAL = 'This prediction does not accept bets withdrawal'
PREDICTION_OPTION_NOT_BET_ON = 'You have not bet on this option'
PREDICTION_STATUS_BETS_HEADER = '*Bets*'
PREDICTION_STATUS_OPTION = '\n\n*{}*. {} ' \
                           '\n*Amount*: ฿{}'
PREDICTION_STATUS_POTENTIAL_WIN = '\n*Potential win*: ฿{}'
PREDICTION_STATUS_RESULT_LOST = '\n*Result*: ' + Emoji.PREDICTION_BET_LOSE.value + 'Lost'
PREDICTION_STATUS_RESULT_LOSS_REFUNDED = ' \\(Refunded\\)'
PREDICTION_STATUS_RESULT_WIN = '\n*Result*: ' + Emoji.PREDICTION_BET_WIN.value + '฿{}'
PREDICTION_STATUS_TOTAL_WIN = '\n\n*Total win*: ' + Emoji.PREDICTION_BET_WIN.value + '฿{}'
PREDICTION_STATUS_NET_WIN = '\n\n*Net win*: ' + Emoji.PREDICTION_BET_WIN.value + '฿{}'
PREDICTION_STATUS_TOTAL_LOSS = '\n\n*Total loss*: ' + Emoji.PREDICTION_BET_LOSE.value + '฿{}'
PREDICTION_STATUS_NET_LOSS = '\n\n*Net loss*: ' + Emoji.PREDICTION_BET_LOSE.value + '฿{}'

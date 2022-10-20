import resources.Environment as Env
import src.model.enums.Command as Command
from src.model.enums.Emoji import Emoji

COMMAND_NOT_IN_REPLY_ERROR = 'This command can only be used in a reply to a message'
COMMAND_IN_REPLY_TO_BOT_ERROR = "This command can't be used in reply to a bot"
COMMAND_IN_REPLY_TO_ERROR = "This command can't be used in a reply to your own message"
COMMAND_NOT_ACTIVE_ERROR = "This command is no longer available"
COMMAND_NOT_ACTIVE_WITH_REPLACEMENT_ERROR = COMMAND_NOT_ACTIVE_ERROR + '. ' + 'Please Use {} instead'
COMMAND_FOR_NEW_WORLD_USERS_ERROR = 'This command is only available for users in the New World'
COMMAND_FOR_USERS_AFTER_LOCATION_ERROR = 'This command is only available for users who have reached *{}*'
COMMAND_WHILE_ARRESTED_ERROR = 'This command is not available while you are arrested'
COMMAND_ONLY_BY_CREW_CAPTAIN_ERROR = 'This command is only available to Crew Captains'
COMMAND_NOT_IN_REPLY_TO_CREW_MEMBER_ERROR = 'This command can only be used in reply to a message from a Crew Member'

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
SHOW_USER_STATUS_ADD_REPLY = '_Requested by {}_'
NOT_ALLOWED_TO_VIEW_REPLIED_STATUS = 'You can only view the status of those who rank below you.' \
                                     '\n\n{} rank: {}' \
                                     '\n{} rank: {}'
ROOKIE_STATUS_PRIVATE_CHAT_ONLY = 'Rookies can only view their status in Private Chat'
PRISONER_STATUS_PRIVATE_CHAT_ONLY = 'Prisoners can only view their status in Private Chat'
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
UNKNOWN_EXTRA_STEP = 'Unknown extra step'
PRIVATE_STEP_NOT_SET = 'Private step not set'

# Keyboard options
KEYBOARD_OPTION_CANCEL = Emoji.CANCEL + ' Cancel'
KEYBOARD_OPTION_DELETE = Emoji.DELETE + ' Delete'
KEYBOARD_OPTION_ACCEPT = Emoji.ACCEPT + ' Accept'
KEYBOARD_OPTION_REJECT = Emoji.REJECT + ' Reject'
KEYBOARD_OPTION_FIGHT = Emoji.FIGHT + ' Fight'
KEYBOARD_OPTION_RETREAT = Emoji.RETREAT + ' Retreat'
KEYBOARD_OPTION_BACK = Emoji.BACK + ' Back'
KEYBOARD_OPTION_YES = Emoji.YES + ' Yes'
KEYBOARD_OPTION_NO = Emoji.NO + ' No'

EXCEPTION_CHAT_ID_NOT_PROVIDED = 'chat_id is None and update.effective_chat.id is None'
EXCEPTION_NO_EDIT_MESSAGE = 'new_message is False but update.callback_query is None'
EXCEPTION_SAVED_MEDIA_UNKNOWN_TYPE = 'Unknown media type: {}'

KEYBOARD_NOT_FOUND = 'Keyboard not found'
KEYBOARD_USE_UNAUTHORIZED = 'You are not authorized to use this keyboard'

LOCATION_LEVEL_UP = '{}Congratulations {}!' \
                    '\nYou are now {} {}' \
                    '\n\n{}'

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

ENABLED = Emoji.ENABLED + ' Enabled'
DISABLED = Emoji.DISABLED + ' Disabled'
ENABLE = Emoji.ENABLED + ' Enable'
DISABLE = Emoji.DISABLED + ' Disable'
CURRENT_SETTING = 'Current setting: {}'

# Private chat
PVT_TXT_START = f'Welcome to @{Env.OPD_GROUP_USERNAME.get()} Bot! From here you can manage your profile.'
PVT_KEY_SETTINGS = Emoji.SETTINGS + ' Settings'
PVT_KEY_STATUS = Emoji.STATUS + ' Status'
PVT_TXT_SETTINGS = 'Which setting would you like to change?'
PVT_KEY_SETTINGS_LOCATION_UPDATE = 'Location update'
PVT_TXT_SETTINGS_LOCATION_UPDATE = 'Do you want to receive an update when you move to a new location?'
PVT_KEY_CREW = Emoji.CREW + ' Crew'
PVT_KEY_CREW_CREATE = 'Create'
PVT_KEY_CREW_LEAVE = 'Leave'
PVT_KEY_CREW_EDIT_NAME = 'Edit name'
PVT_KEY_CREW_DISBAND = 'Disband'
PVT_KEY_SETTINGS_NOTIFICATIONS = 'Notifications'
PVT_TXT_SETTINGS_NOTIFICATIONS = 'Which category of notifications would you like to change?'
PVT_TXT_SETTINGS_NOTIFICATIONS_TYPE = 'Which notification would you like to change?'
PVT_KEY_MANAGE_NOTIFICATION_SETTINGS = 'Manage notification settings'

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
ROCK_PAPER_SCISSORS_CHOICE_ROCK = Emoji.ROCK + ' Rock'
ROCK_PAPER_SCISSORS_CHOICE_PAPER = Emoji.PAPER + ' Paper'
ROCK_PAPER_SCISSORS_CHOICE_SCISSORS = Emoji.SCISSORS + ' Scissors'
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
GAME_RESULT_WIN = Emoji.WINNER + ' {} won'
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
PREDICTION_WAGERS_REFUNDED = f'\n{Emoji.PREDICTION_FEATURE_ENABLED} Wagers refunded'
PREDICTION_MULTIPLE_BETS_ALLOWED = f'\n{Emoji.PREDICTION_FEATURE_ENABLED} Multiple bets allowed'
PREDICTION_CAN_WITHDRAW_BETS = f'\n{Emoji.PREDICTION_FEATURE_ENABLED} Can withdraw bets'
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
PREDICTION_STATUS_RESULT_LOST = '\n*Result*: ' + Emoji.PREDICTION_BET_LOSE + 'Lost'
PREDICTION_STATUS_RESULT_LOSS_REFUNDED = ' \\(Refunded\\)'
PREDICTION_STATUS_RESULT_WIN = '\n*Result*: ' + Emoji.PREDICTION_BET_WIN + '฿{}'
PREDICTION_STATUS_TOTAL_WIN = '\n\n*Total win*: ' + Emoji.PREDICTION_BET_WIN + '฿{}'
PREDICTION_STATUS_NET_WIN = '\n\n*Net win*: ' + Emoji.PREDICTION_BET_WIN + '฿{}'
PREDICTION_STATUS_TOTAL_LOSS = '\n\n*Total loss*: ' + Emoji.PREDICTION_BET_LOSE + '฿{}'
PREDICTION_STATUS_NET_LOSS = '\n\n*Net loss*: ' + Emoji.PREDICTION_BET_LOSE + '฿{}'
PREDICTION_ALL_BETS_REMOVED_FOR_BOUNTY_RESET = 'All bets have been removed for this prediction due to bounty reset'
CHAT_GROUP_MENTION = f'[Chat Group](t.me/{Env.OPD_GROUP_USERNAME.get()})'

# Crew - Private
CREW_USER_NOT_IN_CREW = f'You are not in a Crew. Head over to the {CHAT_GROUP_MENTION} to join' \
                        f' one or create your own.' \
                        f'\n\nTo create a Crew, you must have appeared in the the last ' \
                        f'{Env.CREW_MIN_LATEST_LEADERBOARD_APPEARANCE.get_int()} leaderboards.'
CREW_OVERVIEW = '*{}*\n{}'
CREW_OVERVIEW_MEMBER = '\n{}'
CREW_OVERVIEW_MEMBER_ROLE = f'{CREW_OVERVIEW_MEMBER} ' + '\\({}\\)'
CREW_USER_ALREADY_IN_CREW = 'You are already in a Crew'
CREW_USER_NOT_IN_LATEST_LEADERBOARD_REQUIRED_APPEARANCES = 'You must have appeared in the the last ' \
                                                           f'{Env.CREW_MIN_LATEST_LEADERBOARD_APPEARANCE.get_int()}' \
                                                           f' leaderboards'
CREW_CANNOT_CREATE_CREW = 'You can create a Crew in {}'
CREW_CREATE_REQUEST_NAME = 'Send the name of your Crew'
CREW_CREATE_NAME_ALREADY_EXISTS = 'A Crew with this name already exists'
CREW_CREATE_NAME_TOO_LONG = f'Crew name must be exceed {Env.CREW_NAME_MAX_LENGTH.get_int()} characters'
CREW_CREATE_SUCCESS = 'You are now Captain of the *{}*.' + \
                      f'\n\nHead over to the {CHAT_GROUP_MENTION} to start recruiting members!'
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

# Crew - Invite request
CREW_INVITE_REQUEST_CAPTION = "I'm {} and this meeting must be fate, {}! " \
                              "\nWhat do you say to turning the world upside down with me?"
CREW_INVITE_REQUEST_ACCEPTED = "{} is now a member of {}!"
CREW_INVITE_REQUEST_REJECTED = "Invitation to join the *{}* has been rejected by {}"

STEP_REQUIRES_TEXT = 'Please send a valid text'
ITEM_NOT_FOUND = 'Item not found. If you think this is a mistake, please contact an Admin'

# Crew - Leave
CREW_LEAVE_CONFIRMATION = 'Are you sure you want to leave the Crew?\n' \
                          'You will not be able to join another Crew until the next weekly leaderboard in {}'
CREW_LEAVE_SUCCESS = 'You have left the Crew'

# Crew - Disband
CREW_DISBAND_CONFIRMATION = 'Are you sure you want to disband the Crew?\n' \
                            'You will not be able to create another Crew until the next bounty reset in {}'
CREW_DISBAND_SUCCESS = 'You have disbanded the Crew'

# Notifications - Crew Leave
NOTIFICATION_CATEGORY_CREW = 'Crew'
CREW_LEAVE_NOTIFICATION = '{} has left the Crew'
CREW_LEAVE_NOTIFICATION_DESCRIPTION = 'If to be notified when a member leaves the Crew. ' \
                                      '\nApplicable only if you are the Captain of the Crew.'
CREW_LEAVE_NOTIFICATION_KEY = 'Crew Leave'
# Notifications - Crew Disband
CREW_DISBAND_NOTIFICATION = 'Your Crew has been disbanded'
CREW_DISBAND_NOTIFICATION_DESCRIPTION = 'If to be notified when your Crew is disbanded.'
CREW_DISBAND_NOTIFICATION_KEY = 'Crew Disband'
# Notifications - Crew disband warning
CREW_DISBAND_WARNING_NOTIFICATION = 'You have not appeared in the last {} leaderboards. ' \
                                    '\nIf you do not appear in the next leaderboard, your Crew will be disbanded'
CREW_DISBAND_WARNING_NOTIFICATION_DESCRIPTION = 'If to be notified a week before your Crew is disbanded due to ' \
                                                f'not appearing in the leaderboard for ' \
                                                f'{Env.CREW_MIN_LATEST_LEADERBOARD_APPEARANCE.get_int()} consecutive ' \
                                                f'weeks.' \
                                                '\nApplicable only if you are the Captain of the Crew.'
CREW_DISBAND_WARNING_NOTIFICATION_KEY = 'Crew Disband Warning'
# Notifications - Location
NOTIFICATION_CATEGORY_LOCATION = 'Location'
LOCATION_UPDATE_NOTIFICATION = '{}Congratulations {}!' \
                               '\nYou are now {} {}' \
                               '\n\n{}'
LOCATION_NEXT_LEVEL_REQUIREMENT = '_Requirement for next location: ฿*{}*_'
LOCATION_CURRENT_LEVEL_MAX = '_You have reached the maximum location_'
LOCATION_UPDATE_NOTIFICATION_DESCRIPTION = 'If to be notified when you level up to a new location.'
LOCATION_UPDATE_NOTIFICATION_KEY = 'Location Update'

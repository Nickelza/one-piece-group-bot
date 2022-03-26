from src.model.enums.Command import Command
from src.model.enums.Emoji import Emoji

COMMAND_IN_REPLY_TO_BOT_ERROR = "You can't use this command in a reply to a bot"

SHOW_BOUNTY_DEPRECATED = "This command is no longer available. Please use `/status` instead."
SHOW_USER_STATUS = 'User: {}' \
                   '\nBounty: ฿*{}*' \
                   '\nRank: {}' \
                   '\nLocation: {}'
SHOW_USER_STATUS_ADD_REPLY = '_Requested by {}_'
NOT_ALLOWED_TO_VIEW_REPLIED_STATUS = 'You can only view the status of those who rank below you.' \
                                     '\n\n{} rank: {}' \
                                     '\n{} rank: {}'
BOUNTY_RESET = 'Bounties have been reset'
BOUNTY_RESET_ALERT = 'Bounties will be reset in *{}*'

LEADERBOARD_HEADER = '*Leaderboard* for week *{}* of *{}*\n\nHere are the top {} users with the most bounties:\n'
LEADERBOARD_ROW = '{}°: {}\n{} - ฿*{}*'

SAVE_MEDIA_NOT_IN_REPLY = 'This command can only be used in a reply to a message'
SAVE_MEDIA_NOT_IN_REPLY_TO_MEDIA = 'This command can only be used in a reply to a media message'
SAVED_MEDIA_UNKNOWN_TYPE = 'Unknown media type. Available types are: *{}*'
SAVE_MEDIA_INVALID_FORMAT = 'Invalid format.\n\nCommand: ' + Command.ADM_SAVE_MEDIA.get_formatted() + ' <name>'
SAVE_MEDIA_SUCCESS = 'Media saved as *{}*'

DOC_Q_GAME_NOT_ENOUGH_BOUNTY = 'You need a bounty of at least ฿*{}* to summon Doc Q.' \
                               '\n\n_Current bounty: ฿*{}*_'
DOC_Q_GAME_LIMIT_REACHED = 'You have reached the limit of Doc Q games. You can play again in *{}*'
DOC_Q_GAME_START = 'Hi {}, allow me to offer you an apple.' \
                   '\nIf you choose the right one, you will win ฿*{}*, else you will lose ฿*{}*.' \
                   '\nChoose wisely!' \
                   '\n\n_Current bounty: ฿*{}*_' \
                   '\n_Final bounty if you win: ฿*{}*_' \
                   '\n_Final bounty if you lose: ฿*{}*_'
DOC_Q_GAME_NOT_FOUND = 'Doc Q game not found'
DOC_Q_GAME_NOT_OWNER = "I'm not here for you, call me with {} to play"
DOC_Q_GAME_CANCEL = 'See you next time!'
DOC_Q_GAME_WIN = "You're...haha...cough! cough! a really lucky one {}." \
                 "\nLet's go, Stronger...agh..!" \
                 "\n\n_{}You won ฿*{}*!_" \
                 "\n_Current bounty: ฿*{}*_"
DOC_Q_GAME_LOSE = "Seems like today wasn't your lucky day {}...cough!...better luck next time." \
                  "\nLet's go, Stronger...agh..!" \
                  "\n\n_{}You lost ฿*{}*._" \
                  "\n_Current bounty: ฿*{}*_"

# Error messages
USER_NOT_FOUND = 'User not found'
UNRECOGNIZED_SCREEN = 'Unrecognized command'
DOC_Q_MEDIA_NOT_FOUND = 'Doc Q Media not found'

# Keyboard options
KEYBOARD_OPTION_CANCEL = Emoji.CANCEL.value + ' Cancel'
KEYBOARD_OPTION_DELETE = Emoji.CANCEL.value + ' Delete'
KEYBOARD_OPTION_ACCEPT = Emoji.ACCEPT.value + ' Accept'
KEYBOARD_OPTION_REJECT = Emoji.REJECT.value + ' Reject'

EXCEPTION_CHAT_ID_NOT_PROVIDED = 'chat_id is None and update.effective_chat.id is None'
EXCEPTION_NO_EDIT_MESSAGE = 'new_message is False but update.callback_query is None'
EXCEPTION_SAVED_MEDIA_UNKNOWN_TYPE = 'Unknown media type: {}'

KEYBOARD_NOT_FOUND = 'Keyboard not found'
KEYBOARD_USE_UNAUTHORIZED = 'You are not authorized to use this keyboard'

PVT_CHAT_START = 'Welcome to @onepiecegroup Bot!'

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

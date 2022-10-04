from telegram import Update
from telegram.ext import CallbackContext

import resources.Environment as Env
import resources.phrases as phrases
import src.model.enums.Command as Command
from src.model.User import User
from src.model.enums import Location
from src.model.enums.Region import Region
from src.model.enums.Screen import Screen
from src.model.error.GroupChatError import GroupChatError
from src.model.pojo.Keyboard import Keyboard
from src.service.bounty_service import get_belly_formatted
from src.service.cron_service import cron_datetime_difference
from src.service.location_service import update_location
from src.service.message_service import full_message_send, mention_markdown_v2, get_image_preview, get_yes_no_keyboard


def validate_move_request(update: Update, context: CallbackContext, user: User, destination_region: Region) -> bool:
    """
    Validate the move request
    :param update: The update
    :param context: The context
    :param user: The user
    :param destination_region: The region to move to
    :return: True if the move is valid
    """
    # User is already in requested region
    location: Location = Location.get_by_level(user.location_level)
    if location.region == destination_region:
        ot_text = phrases.LOCATION_ALREADY_IN_REGION.format(get_region_text(destination_region))
        full_message_send(context, ot_text, update=update, add_delete_button=True)
        return False

    # User cannot change region
    if not user.can_change_region:
        ot_text = phrases.LOCATION_CANNOT_CHANGE_REGION.format(
            cron_datetime_difference(Env.CRON_RESET_CAN_CHANGE_REGION.get()))
        full_message_send(context, ot_text, update, add_delete_button=True)
        return False

    # Not enough bounty for New World
    if destination_region == Region.NEW_WORLD:
        first_new_world_location: Location = Location.get_first_new_world()
        if user.bounty < first_new_world_location.required_bounty:
            ot_text = phrases.LOCATION_NEW_WORLD_REQUEST_REJECTED_NOT_ENOUGH_BOUNTY.format(
                get_belly_formatted(first_new_world_location.required_bounty))
            full_message_send(context, ot_text, update=update, add_delete_button=True)
            return False

    return True


def get_region_text(region: Region) -> str:
    return 'Paradise' if region == region.PARADISE else 'the New World'


def get_region_image_preview(region: Region) -> str:
    if region == Region.PARADISE:
        return get_image_preview(Env.LOCATION_PARADISE_IMAGE_URL.get())
    elif region == Region.NEW_WORLD:
        return get_image_preview(Env.LOCATION_NEW_WORLD_IMAGE_URL.get())
    else:
        return ''


def send_proposal(update: Update, context: CallbackContext, user: User, region: Region) -> None:
    """
    Send proposal for region change
    :param update: The update object
    :param context: The context object
    :param user: The user object
    :param region: The region to move to
    :return: None
    """

    if region == Region.ND:
        full_message_send(context, GroupChatError.INVALID_CHANGE_REGION_REQUEST.build(), update)
        return

    ot_text = phrases.LOCATION_CHANGE_REGION_PROPOSAL.format(get_region_image_preview(region),
                                                             mention_markdown_v2(user.tg_user_id, user.tg_first_name),
                                                             get_region_text(region))
    # Keyboard
    inline_keyboard: list[list[Keyboard]] = [get_yes_no_keyboard(user, region, phrases.KEYBOARD_OPTION_ACCEPT,
                                                                 phrases.KEYBOARD_OPTION_REJECT,
                                                                 Screen.GRP_CHANGE_REGION)]

    full_message_send(context, ot_text, update=update, keyboard=inline_keyboard, disable_web_page_preview=False)


def keyboard_interaction(update: Update, context: CallbackContext, user: User, keyboard: Keyboard, region: Region
                         ) -> None:
    """
    Keyboard interaction
    :param update: The update
    :param context: The context
    :param user: The user
    :param keyboard: The keyboard
    :param region: The region
    :return: None
    """

    # User accepted
    if keyboard.info['b'] == 1:
        # Verify that user can move
        if not validate_move_request(update, context, user, region):
            return

        # Refresh location
        user = update_location(context, user, update, cap_to_paradise=False, region=region, requested_by_user=True)
        user.can_change_region = False
        user.save()
        return

    else:  # User rejected
        command: Command.Command = Command.GRP_CHANGE_REGION_PARADISE if region == Region.PARADISE else \
            Command.GRP_CHANGE_REGION_NEW_WORLD
        ot_text = phrases.LOCATION_CHANGE_REGION_PROPOSAL_REJECTED.format(
            get_region_image_preview(region),
            mention_markdown_v2(user.tg_user_id, user.tg_first_name),
            get_region_text(region),
            command.get_formatted())
        full_message_send(context, ot_text, update=update, add_delete_button=True)
        return


def manage(update: Update, context: CallbackContext, user: User, keyboard: Keyboard = None,
           command: Command.Command = None) -> None:
    """
    Manage the change region request
    :param update: The update object
    :param context: The context object
    :param user: The user object
    :param keyboard: The keyboard object
    :param command: The command message
    :return: None
    """

    # Move to new world request
    if keyboard is not None:
        region = Region(keyboard.info['a'])
    elif command is not None:
        region = Region.PARADISE if command == Command.GRP_CHANGE_REGION_PARADISE else Region.NEW_WORLD
    else:
        full_message_send(context, GroupChatError.INVALID_CHANGE_REGION_REQUEST.build(), update)
        return

    if not validate_move_request(update, context, user, region):
        return

    # Request to move
    if keyboard is None:
        send_proposal(update, context, user, region)
        return

    # Interaction with keyboard
    if keyboard is None:
        full_message_send(context, GroupChatError.KEYBOARD_NOT_FOUND.build(), update)
        return

    keyboard_interaction(update, context, user, keyboard, region)

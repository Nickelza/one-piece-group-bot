from peewee import Case
from telegram import Update, Message
from telegram.ext import CallbackContext

import resources.phrases as phrases
from src.chat.group.screens.screen_status import send_bounty_poster
from src.model.User import User
from src.model.UserLocationBountyPoster import UserLocationBountyPoster
from src.model.enums import Location
from src.model.enums.Region import Region
from src.service.message_service import full_message_send, get_image_preview, mention_markdown_v2


def update_location(context: CallbackContext, user: User, update: Update = None, cap_to_paradise: bool = True,
                    send_update_message: bool = False, region: Region = None) -> User:
    """
    Refresh the location of the user
    :param context: Telegram context
    :param user: The user object
    :param update: Telegram update
    :param cap_to_paradise: If the move should be capped to Paradise max level when user is in Paradise
    :param send_update_message: If the update message should be sent
    :param region: The region to move the user to
    :return: The user object
    """

    from src.chat.group.screens.screen_change_region import send_proposal as send_new_world_proposal
    from src.service.bounty_service import get_bounty_formatted

    # Get location that corresponds to the user current bounty
    new_location: Location = Location.get_by_bounty(user.bounty)

    # User can level up
    if region is not None or new_location.level > user.location_level:
        effective_location: Location = new_location

        # Cap the location level to Paradise max
        if region == Region.PARADISE or (Location.is_paradise_by_level(user.location_level)
                                         and Location.is_new_world_by_level(new_location.level) and cap_to_paradise):
            effective_location: Location = Location.get_last_paradise()

        # Show level up message
        try:
            next_location = Location.get_by_level(effective_location.level + 1)
            ot_text_suffix = phrases.LOCATION_NEXT_LEVEL_REQUIREMENT.format(
                get_bounty_formatted(next_location.required_bounty))
        except ValueError:
            ot_text_suffix = phrases.LOCATION_CURRENT_LEVEL_MAX

        if user.location_level != effective_location.level and send_update_message:

            # Determine preposition to use for the location
            if 'island' in effective_location.name.lower() or 'archipelago' in effective_location.name.lower():
                preposition = 'on'
                if effective_location.name.lower().startswith('island'):
                    preposition += ' the'
            else:
                preposition = 'in'

            ot_text = phrases.LOCATION_LEVEL_UP.format(get_image_preview(effective_location.image_url),
                                                       mention_markdown_v2(user.tg_user_id, user.tg_first_name),
                                                       preposition,
                                                       effective_location.name,
                                                       ot_text_suffix)

            message: Message = full_message_send(context, ot_text, update=update, disable_web_page_preview=False,
                                                 add_delete_button=True)

            # Should send poster if it hasn't been sent for this location ever
            if effective_location.show_poster:
                user_location_bounty_poster: UserLocationBountyPoster = UserLocationBountyPoster.get_or_none(
                    (UserLocationBountyPoster.user == user)
                    & (UserLocationBountyPoster.location_level == effective_location.level))
                if user_location_bounty_poster is None and send_update_message:
                    send_bounty_poster(context, update, user, reply_to_message_id=message.message_id)

                # Save the poster as sent for this location
                user_location_bounty_poster: UserLocationBountyPoster = UserLocationBountyPoster()
                user_location_bounty_poster.user = user
                user_location_bounty_poster.location_level = effective_location.level
                user_location_bounty_poster.save()

        # Update user location
        user.location_level = effective_location.level
        user.save()

    # Move to New World proposal
    if new_location.region == Region.NEW_WORLD and user.location_level == Location.get_last_paradise().level \
            and user.should_propose_new_world:
        send_new_world_proposal(update, context, user, Region.NEW_WORLD)
        user.should_propose_new_world = False
        user.save()

    return user


def reset_location() -> None:
    """
    Reset the user's location
    :return: None
    """

    # Update user location
    conditions: list[tuple[bool, int]] = []
    for location in reversed(Location.LOCATIONS):
        conditions.append((User.bounty >= location.required_bounty, location.level))
    case_stmt = Case(None, conditions)
    User.update(location_level=case_stmt).execute()

    # Reset new world proposal
    User.update(should_propose_new_world=True).where(User.should_propose_new_world is False).execute()


def reset_can_change_region(context: CallbackContext) -> None:
    """
    Reset the user's can_change_region flag
    :param context:
    :return: None
    """

    User.update(can_change_region=True).where(User.can_change_region is True).execute()

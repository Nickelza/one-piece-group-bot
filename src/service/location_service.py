from peewee import Case
from telegram import Update
from telegram.ext import ContextTypes

import resources.Environment as Env
from src.model.User import User
from src.model.enums import Location
from src.model.enums.Notification import LocationUpdateNotification
from src.model.enums.Region import Region
from src.service.message_service import full_message_send
from src.service.notification_service import send_notification


async def update_location(user: User, context: ContextTypes.DEFAULT_TYPE = None, update: Update = None,
                          cap_to_paradise: bool = True, region: Region = None, requested_by_user: bool = False,
                          can_scale_down: bool = False, should_passive_update: bool = False) -> None:
    """
    Refresh the location of the user
    :param user: The user object
    :param context: Telegram context
    :param update: Telegram update
    :param cap_to_paradise: If the move should be capped to Paradise max level when user is in Paradise
    :param region: The region to move the user to
    :param requested_by_user: If the user requested the update
    :param can_scale_down: If the new location can be lower than the current one
    :param should_passive_update: If the update should be passive, without any output message
    :return: The user object
    """

    from src.chat.group.screens.screen_change_region import send_proposal as send_new_world_proposal

    # Get location that corresponds to the user current bounty
    new_location: Location = Location.get_by_bounty(user.get_max_bounty())

    # User can level up
    if region is not None or new_location.level > user.location_level or can_scale_down:
        effective_location: Location = new_location

        # Cap the location level to Paradise max
        if region is Region.PARADISE or (Location.is_paradise_by_level(user.location_level)
                                         and Location.is_new_world_by_level(new_location.level) and cap_to_paradise):
            effective_location: Location = Location.get_last_paradise()

        if user.location_level != effective_location.level and not should_passive_update:
            location_update_notification: LocationUpdateNotification = LocationUpdateNotification(user,
                                                                                                  effective_location)
            if requested_by_user:  # Update after region change, edit group message
                await full_message_send(context, location_update_notification.build(), update=update,
                                        disable_web_page_preview=False, add_delete_button=True)
            elif Env.SEND_MESSAGE_LOCATION_UPDATE.get_bool():  # Update after bounty change, send notification
                await send_notification(context, user, location_update_notification)

        # Update user location
        user.location_level = effective_location.level

    # Move to New World proposal
    if (not should_passive_update  # Update not from user interaction in group
            and new_location.region == Region.NEW_WORLD  # Location relative to bounty is in New World
            and user.location_level == Location.get_last_paradise().level  # Capped location is last of Paradise
            and user.should_propose_new_world  # User has not been proposed to move to New World yet
            and (requested_by_user  # User requested the update
                 or Env.SEND_MESSAGE_MOVE_TO_NEW_WORLD_PROPOSAL.get_bool())):  # Auto proposal enabled
        await send_new_world_proposal(update, context, user, Region.NEW_WORLD)
        user.should_propose_new_world = False


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


def reset_can_change_region() -> None:
    """
    Reset the user's can_change_region flag

    :return: None
    """

    User.update(can_change_region=True).where(User.can_change_region is False).execute()

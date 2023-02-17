from telegram import Update
from wantedposter.wantedposter import WantedPoster, VerticalAlignment, CaptureCondition

import constants as c
from src.model.Leaderboard import Leaderboard
from src.model.LeaderboardUser import LeaderboardUser
from src.model.User import User
from src.model.enums.LeaderboardRank import LeaderboardRank, get_rank_by_index
from src.service.devil_fruit_service import user_has_eaten_devil_fruit
from src.service.download_service import generate_temp_file_path


async def get_bounty_poster(update: Update, user: User) -> str:
    """
    Gets the bounty poster of a user
    :param update: Telegram update
    :param user: The user to get the poster of
    :return: The path to the poster
    """

    from src.service.user_service import get_user_profile_photo, user_is_boss

    wanted_poster = WantedPoster(portrait=await get_user_profile_photo(update),
                                 first_name=user.tg_first_name,
                                 last_name=user.tg_last_name,
                                 bounty=user.bounty)

    capture_condition: CaptureCondition = CaptureCondition.DEAD_OR_ALIVE

    if user_has_eaten_devil_fruit(user):
        capture_condition = CaptureCondition.ONLY_ALIVE

    if user_is_boss(user):
        capture_condition = CaptureCondition.ONLY_DEAD

    return wanted_poster.generate(output_poster_path=generate_temp_file_path(c.BOUNTY_POSTER_EXTENSION),
                                  portrait_vertical_align=VerticalAlignment.TOP, capture_condition=capture_condition)


def get_bounty_poster_limit(leaderboard_user: LeaderboardUser) -> int:
    """
    Gets the bounty poster limit of a user by their leaderboard position
    :param leaderboard_user: The user to get the bounty poster limit of
    :return: The bounty poster limit of the user
    """

    leaderboard_rank: LeaderboardRank = get_rank_by_index(leaderboard_user.rank_index)
    return leaderboard_rank.bounty_poster_limit


async def reset_bounty_poster_limit(reset_previous_leaderboard: bool = False) -> None:
    """
    Resets the bounty poster limit

    :param reset_previous_leaderboard: If to reset the limit for users if the previous leaderboard
    """

    from src.service.leaderboard_service import get_leaderboard

    if reset_previous_leaderboard:
        # Reset the limit for users
        previous_leaderboard: Leaderboard = get_leaderboard(1)
        previous_leaderboard_users_id = LeaderboardUser.select(LeaderboardUser.user) \
            .where(LeaderboardUser.leaderboard == previous_leaderboard)
        if previous_leaderboard is not None:
            User.update(bounty_poster_limit=0).where(User.id.in_(previous_leaderboard_users_id)).execute()

    # Reset the limit for the current leaderboard users
    current_leaderboard: Leaderboard = get_leaderboard()
    if current_leaderboard is not None:
        for leaderboard_user in current_leaderboard.leaderboard_users:
            leaderboard_user: LeaderboardUser = leaderboard_user

            User.update(bounty_poster_limit=get_bounty_poster_limit(leaderboard_user)) \
                .where(User.id == leaderboard_user.user).execute()

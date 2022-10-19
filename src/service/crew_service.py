from datetime import datetime

from src.model.Crew import Crew
from src.model.User import User
from src.model.enums.CrewRole import CrewRole


def add_member(user: User, crew: Crew, role: CrewRole = None) -> None:
    """
    Adds a member to a crew

    :param user: The user
    :param crew: The crew
    :param role: The role
    """

    user.crew = crew
    user.crew_role = role
    user.crew_join_date = datetime.now()
    user.save()


def remove_member(user) -> None:
    """
    Removes a member from a crew

    :param user: The user
    :return: None
    """

    user.crew = None
    user.crew_role = None
    user.crew_join_date = None
    user.can_join_crew = False
    user.save()

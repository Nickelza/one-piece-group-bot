from datetime import datetime

import resources.phrases as phrases
from src.model.Crew import Crew
from src.model.User import User
from src.model.enums.CrewRole import CrewRole
from src.model.error.CustomException import CrewValidationException
from src.model.pojo.Keyboard import Keyboard


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


def get_crew(user: User = None, crew_id: int = None, inbound_keyboard: Keyboard = None, crew_id_key: str = None
             ) -> Crew:
    """
    Get crew
    :param user: The target user
    :param crew_id: The crew id
    :param inbound_keyboard: The inbound keyboard
    :param crew_id_key: The crew id key
    :return: The crew
    """

    if user is None and crew_id is None and inbound_keyboard is None:
        raise ValueError('Either user or crew_id or inbound_keyboard must be provided')

    if inbound_keyboard is not None and crew_id_key is None:
        raise ValueError('crew_id_key must be provided if inbound_keyboard is provided')

    if inbound_keyboard is not None:  # Can use "else", used "elif" to avoid IDE warning
        crew: Crew = Crew.logical_get(inbound_keyboard.info[crew_id_key])
    elif user is not None:
        crew: Crew = user.crew
    else:
        crew: Crew = Crew.logical_get(crew_id)

    # Crew is not found or is not active
    if crew is None or not crew.is_active:
        raise CrewValidationException(phrases.CREW_NOT_FOUND)

    return crew

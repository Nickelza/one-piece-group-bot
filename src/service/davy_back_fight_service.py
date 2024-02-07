from resources import phrases
from src.model.Crew import Crew
from src.model.DavyBackFight import DavyBackFight
from src.model.DavyBackFightParticipant import DavyBackFightParticipant
from src.model.User import User
from src.model.enums.GameStatus import GameStatus
from src.model.error.CustomException import CrewValidationException


def add_participant(user: User, davy_back_fight: DavyBackFight):
    """
    Add a participant to the Davy Back Fight
    :param user: The user object
    :param davy_back_fight: The Davy Back Fight object
    :return: None
    """

    crew: Crew = user.crew

    # Davy Back Fight not in countdown
    if davy_back_fight.get_status() is not GameStatus.COUNTDOWN_TO_START:
        raise CrewValidationException(phrases.ITEM_IN_WRONG_STATUS)

    # User not in a participating crew
    if crew not in [davy_back_fight.challenger_crew, davy_back_fight.opponent_crew]:
        raise CrewValidationException(
            phrases.CREW_DAVY_BACK_FIGHT_USER_NOT_MEMBER_OF_PARTICIPATING_CREW
        )

    # Already a participant
    if user in davy_back_fight.get_participants(crew=crew):
        raise CrewValidationException(phrases.CREW_DAVY_BACK_FIGHT_USER_ALREADY_PARTICIPANT)

    # Add participant
    participant: DavyBackFightParticipant = DavyBackFightParticipant()
    participant.davy_back_fight = davy_back_fight
    participant.user = user
    participant.crew = crew
    participant.save()


def set_default_participants(crew: Crew, davy_back_fight: DavyBackFight) -> None:
    """
    Set the default participants for a Davy Back Fight
    :param crew: The crew object
    :param davy_back_fight: The Davy Back Fight object
    :return: None
    """

    # Crew does not have enough members
    if crew.get_member_count() < davy_back_fight.participants_count:
        raise CrewValidationException(phrases.CREW_DAVY_BACK_FIGHT_NOT_ENOUGH_MEMBERS)

    # Delete existing participants
    DavyBackFightParticipant.delete().where(
        (DavyBackFightParticipant.davy_back_fight == davy_back_fight)
        & (DavyBackFightParticipant.crew == crew)
    ).execute()

    # Add participants
    for index, user in enumerate(crew.get_members()):
        if index >= davy_back_fight.participants_count:
            break
        add_participant(user=user, davy_back_fight=davy_back_fight)

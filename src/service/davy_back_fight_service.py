import datetime

from telegram.ext import CallbackContext, ContextTypes

import resources.Environment as Env
from resources import phrases
from src.model.Crew import Crew
from src.model.DavyBackFight import DavyBackFight
from src.model.DavyBackFightParticipant import DavyBackFightParticipant
from src.model.User import User
from src.model.enums.GameStatus import GameStatus
from src.model.enums.Notification import (
    DavyBackFightStartNotification,
    DavyBackFightEndNotification,
)
from src.model.enums.income_tax.IncomeTaxEventType import IncomeTaxEventType
from src.model.error.CustomException import CrewValidationException
from src.model.game.GameOutcome import GameOutcome
from src.service.date_service import get_datetime_in_future_days
from src.service.notification_service import send_notification


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


def swap_participant(
    davy_back_fight: DavyBackFight, old_participant: User, new_participant: User
) -> None:
    """
    Swap a participant
    :param davy_back_fight: The Davy Back Fight object
    :param old_participant: The old participant object
    :param new_participant: The new participant object
    :return: None
    """

    # Remove old participant
    DavyBackFightParticipant.delete().where(
        (DavyBackFightParticipant.davy_back_fight == davy_back_fight)
        & (DavyBackFightParticipant.user == old_participant)
    ).execute()

    # Add new participant
    add_participant(new_participant, davy_back_fight)


async def start_all(context: ContextTypes.DEFAULT_TYPE):
    """
    Start all the Davy Back Fights
    :param context: The context object
    :return: None
    """

    for davy_back_fight in DavyBackFight.select().where(
        (DavyBackFight.status == GameStatus.COUNTDOWN_TO_START)
        & (DavyBackFight.start_date < datetime.datetime.now())
    ):
        context.application.create_task(start(context, davy_back_fight))


async def start(context: CallbackContext, davy_back_fight: DavyBackFight):
    """
    Start a Davy Back Fight
    :param context: The context object
    :param davy_back_fight: The Davy Back Fight object
    :return: None
    """

    davy_back_fight.status = GameStatus.IN_PROGRESS
    davy_back_fight.save()

    # Send notification to players
    for participant in davy_back_fight.get_participants():
        await send_notification(
            context,
            participant.user,
            DavyBackFightStartNotification(
                davy_back_fight.get_opponent_crew(participant.crew), davy_back_fight
            ),
        )


async def add_contribution(user: User, amount: int, opponent: User = None):
    """
    Add contribution to the Davy Back Fight
    :param user: The user object
    :param amount: The amount
    :param opponent: The opponent from which bounty is taken
    :return: None
    """
    crew: Crew = user.crew

    dbf: DavyBackFight = crew.get_in_progress_davy_back_fight()

    # Crew not in an active Davy Back Fight
    if dbf is None:
        return

    participant: DavyBackFightParticipant = dbf.get_participant(user)

    # User not a participant
    if participant is None:
        return

    # By default, always valued at 50% apart from case in which opponent is an adversary.
    # Halving here to preemptively manage cases in which opponent is not provided, for example
    # Doc Q

    amount //= 2
    if opponent is not None:
        # Bounty gained from fellow Crew members is not counted
        if opponent.crew == crew:
            return

        # Bounty gained from someone that's not a participant is valued at 100%
        if dbf.is_participant(opponent):
            amount *= 2

    participant.contribution += amount
    participant.save()


async def end_all(context: ContextTypes.DEFAULT_TYPE):
    """
    End all the Davy Back Fights
    :param context: The context object
    :return: None
    """

    for davy_back_fight in DavyBackFight.select().where(
        (DavyBackFight.status == GameStatus.IN_PROGRESS)
        & (DavyBackFight.end_date < datetime.datetime.now())
    ):
        context.application.create_task(end(context, davy_back_fight))


async def end(context: CallbackContext, davy_back_fight: DavyBackFight):
    """
    End a Davy Back Fight
    :param context: The context object
    :param davy_back_fight: The Davy Back Fight object
    :return: None
    """
    from src.service.bounty_service import add_or_remove_bounty

    outcome: GameOutcome = davy_back_fight.get_outcome()
    if outcome is GameOutcome.CHALLENGER_WON:
        winner_crew = davy_back_fight.challenger_crew
        davy_back_fight.status = GameStatus.WON
    else:
        winner_crew = davy_back_fight.opponent_crew
        davy_back_fight.status = GameStatus.LOST

    davy_back_fight.penalty_end_date = get_datetime_in_future_days(
        Env.DAVY_BACK_FIGHT_LOSE_PENALTY_DURATION.get_int(), start_time=davy_back_fight.end_date
    )
    davy_back_fight.save()

    # Send notification to players
    participants: list[DavyBackFightParticipant] = davy_back_fight.get_participants()
    for participant in participants:
        if participant.crew == winner_crew:
            participant.win_amount = participant.get_win_amount()
            participant.save()

        # Add amount
        context.application.create_task(
            add_or_remove_bounty(
                participant.user,
                amount=participant.win_amount,
                context=context,
                should_save=True,
                tax_event_type=IncomeTaxEventType.DAVY_BACK_FIGHT,
                event_id=davy_back_fight.id,
            )
        )

        await send_notification(
            context,
            participant.user,
            DavyBackFightEndNotification(
                davy_back_fight.get_opponent_crew(participant.crew), participant
            ),
        )

import datetime

from peewee import *

import resources.Environment as Env
from src.model.BaseModel import BaseModel
from src.model.Crew import Crew
from src.model.User import User
from src.model.enums.GameStatus import GameStatus
from src.model.enums.income_tax.IncomeTaxEventType import IncomeTaxEventType
from src.model.game.GameOutcome import GameOutcome
from src.service.date_service import datetime_is_after, get_remaining_duration
from src.service.string_service import get_belly_formatted


class DavyBackFight(BaseModel):
    """
    DavyBackFight class
    """

    id: int | PrimaryKeyField = PrimaryKeyField()
    challenger_crew: Crew | ForeignKeyField = ForeignKeyField(
        Crew, backref="davy_back_fights_challengers"
    )
    opponent_crew: Crew | ForeignKeyField = ForeignKeyField(
        Crew, backref="davy_back_fights_opponents"
    )
    challenger_chest: int | BigIntegerField = BigIntegerField(default=0)
    opponent_chest: int | BigIntegerField = BigIntegerField(default=0)
    participants_count: int | IntegerField = IntegerField()
    duration_hours: int | IntegerField = IntegerField()
    penalty_days = IntegerField()
    date = DateTimeField(default=datetime.datetime.now)
    status: int | SmallIntegerField = SmallIntegerField(
        default=GameStatus.AWAITING_OPPONENT_CONFIRMATION
    )
    start_date: datetime.datetime | DateTimeField = DateTimeField(null=True)
    end_date: datetime.datetime | DateTimeField = DateTimeField(null=True)
    conscript: User | ForeignKeyField = ForeignKeyField(
        User, backref="davy_back_fights_conscripts", null=True
    )
    conscript_date: datetime.datetime | DateTimeField = DateTimeField(null=True)
    penalty_end_date: datetime.datetime | DateTimeField = DateTimeField(null=True)
    penalty_payout: int | BigIntegerField = BigIntegerField(default=0)

    class Meta:
        db_table = "davy_back_fight"

    @staticmethod
    async def delete_expired_requests():
        """
        Delete expire requests, so requests that are in AWAITING_OPPONENT_CONFIRMATION status and
        were created more than x minutes ago
        """
        DavyBackFight.delete().where(
            DavyBackFight.status == GameStatus.AWAITING_OPPONENT_CONFIRMATION,
            DavyBackFight.date
            < (
                datetime.datetime.now()
                - datetime.timedelta(minutes=Env.DAVY_BACK_FIGHT_REQUEST_EXPIRATION_TIME.get_int())
            ),
        ).execute()

    def get_participants(self, crew: Crew = None) -> list[any]:
        """
        Get all the participants of a Davy Back Fight
        :param crew: The crew object
        :return: The list of participants
        """

        if crew is None:
            return self.davy_back_fight_participants

        return [p for p in self.davy_back_fight_participants if p.crew == crew]

    def get_participants_users(self, crew: Crew = None) -> list[User]:
        """
        Get all the participants of a Davy Back Fight
        :param crew: The crew object
        :return: The list of participants
        """

        if crew is None:
            return [p.user for p in self.davy_back_fight_participants]

        return [p.user for p in self.davy_back_fight_participants if p.crew == crew]

    def get_non_participants_users(self, crew: Crew) -> list[any]:
        """
        Get all the non-participants of a Davy Back Fight
        :param crew: The crew object
        :return: The list of non-participants
        """
        return [m for m in crew.get_members() if m not in self.get_participants_users(crew=crew)]

    def get_status(self) -> GameStatus:
        """
        Get the status of the Davy Back Fight
        :return: The status
        """

        return GameStatus(self.status)

    def in_progress(self) -> bool:
        """
        Check if the game is in progress
        :return: True if the game is in progress, False otherwise
        """
        return self.get_status() is GameStatus.IN_PROGRESS

    def has_ended(self) -> bool:
        """
        Check if the game has ended
        :return: True if the game has ended, False otherwise
        """
        return self.get_status().is_finished()

    def get_crew_gain(self, crew: Crew) -> int:
        """
        Get the crew gain
        :param crew: The crew object
        :return: The crew gain
        """

        return sum([p.contribution for p in self.davy_back_fight_participants if p.crew == crew])

    def get_opponent_crew(self, crew: Crew):
        """
        Get the opponent crew
        :param crew: The crew object
        :return: The opponent crew
        """

        if crew == self.challenger_crew:
            return self.opponent_crew
        return self.challenger_crew

    def get_in_progress_display_status(self, crew: Crew) -> GameStatus:
        """
        Get the in progress display status [WINNING, LOSING, DRAW]
        :param crew: The crew object
        :return: The in progress display status
        """

        crew_total = self.get_crew_gain(crew)
        opponent_total = self.get_crew_gain(self.get_opponent_crew(crew))

        if crew_total > opponent_total:
            return GameStatus.WINNING

        if crew_total < opponent_total:
            return GameStatus.LOSING

        return GameStatus.DRAW

    def get_participant(self, user: User) -> any:
        """
        Get the participant
        :param user: The user object
        :return: The participant
        """
        from src.model.DavyBackFightParticipant import DavyBackFightParticipant

        return self.davy_back_fight_participants.where(
            DavyBackFightParticipant.user == user
        ).get_or_none()

    def is_participant(self, user: User) -> bool:
        """
        Check if the user is a participant
        :param user: The user object
        :return: True if the user is a participant, False otherwise
        """
        return self.get_participant(user) is not None

    @staticmethod
    def get_contribution_events() -> list[IncomeTaxEventType]:
        """
        Get the tax events that generate a DBF contribution
        :return: The contribution events
        """
        return [IncomeTaxEventType.GAME, IncomeTaxEventType.FIGHT, IncomeTaxEventType.PLUNDER]

    def get_chest_amount(self, crew: Crew) -> int:
        """
        Get the chest amount
        :param crew: The crew object
        :return: The chest amount
        """
        if crew == self.challenger_crew:
            return self.challenger_chest
        return self.opponent_chest

    def get_opponent_chest_amount(self, crew: Crew) -> int:
        """
        Get the chest amount
        :param crew: The crew object
        :return: The chest amount
        """

        return self.get_chest_amount(self.get_opponent_crew(crew))

    def get_winner_crew(self) -> Crew | None:
        """
        Get the winner
        :return: The winner
        """
        if self.get_status() not in [GameStatus.WON, GameStatus.LOST]:
            return None

        if self.get_status() is GameStatus.WON:
            return self.challenger_crew

        return self.opponent_crew

    def is_winner_crew(self, crew: Crew) -> bool:
        """
        Check if the crew is the winner
        :param crew: The crew object
        :return: True if the crew is the winner, False otherwise
        """
        return self.get_winner_crew() == crew

    def get_remaining_time(self) -> str:
        from src.service.date_service import get_remaining_duration

        return get_remaining_duration(self.end_date)

    def get_outcome(self) -> GameOutcome:
        """
        Get the outcome of the game
        :return: The outcome
        """
        from src.model.DavyBackFightParticipant import DavyBackFightParticipant

        if DavyBackFightParticipant.get_total_contributions(
            self, self.challenger_crew
        ) >= DavyBackFightParticipant.get_total_contributions(self, self.opponent_crew):
            return GameOutcome.CHALLENGER_WON

        return GameOutcome.OPPONENT_WON

    def get_penalty_payout(self):
        """
        Get the penalty payout
        :return: The penalty payout
        """
        if self.get_status() is GameStatus.WON:
            return self.challenger_chest + self.penalty_payout

        return self.opponent_chest + self.penalty_payout

    def get_penalty_payout_formatted(self):
        """
        Get the penalty payout formatted
        :return: The penalty payout formatted
        """
        return get_belly_formatted(self.get_penalty_payout())

    def in_penalty_period(self) -> bool:
        """
        Check if the game is in penalty period
        :return: True if the game is in penalty period, False otherwise
        """
        return datetime_is_after(self.penalty_end_date)

    def get_penalty_remaining_time(self) -> str:
        """
        Get the penalty remaining time
        :return: The penalty remaining time
        """

        return get_remaining_duration(self.penalty_end_date)

    @staticmethod
    def get_max_participants(challenger_crew: Crew, opponent_crew: Crew) -> int:
        """
        Get the max participants
        :param challenger_crew: The challenger crew
        :param opponent_crew: The opponent crew
        :return: The max participants
        """
        return min(challenger_crew.get_member_count(), opponent_crew.get_member_count())


DavyBackFight.create_table()

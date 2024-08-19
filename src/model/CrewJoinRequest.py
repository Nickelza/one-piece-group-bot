import datetime

from peewee import *

import resources.Environment as Env
from src.model.BaseModel import BaseModel
from src.model.Crew import Crew
from src.model.User import User
from src.model.enums.crew.CrewJoinRequestStatus import CrewJoinRequestStatus


class CrewJoinRequest(BaseModel):
    """
    CrewJoinRequest class
    """

    user: User | ForeignKeyField = ForeignKeyField(User, backref="crew_join_requests")
    crew: Crew | ForeignKeyField = ForeignKeyField(Crew, backref="crew_join_requests")
    status: CrewJoinRequestStatus | SmallIntegerField = SmallIntegerField(
        default=CrewJoinRequestStatus.PENDING
    )

    class Meta:
        db_table = "crew_join_request"

    @staticmethod
    def get_all_requests_in_cooldown_period(user: User) -> list["CrewJoinRequest"]:
        """
        Get all requests of a user in the cooldown period
        :param user: The user object
        :return: The list of requests
        """
        return (
            CrewJoinRequest.select()
            .where(
                CrewJoinRequest.user == user,
                CrewJoinRequest.date
                > datetime.datetime.now()
                - datetime.timedelta(hours=Env.CREW_JOIN_REQUEST_COOLDOWN_DURATION.get_int()),
            )
            .order_by(CrewJoinRequest.date.asc())
        )

    @staticmethod
    def get_all_requests_in_cooldown_period_for_crew(
        user: User, crew: Crew
    ) -> list["CrewJoinRequest"]:
        """
        Get all requests of a user for a given crew in the cooldown period
        :param user: The user object
        :param crew: The crew object
        :return: The list of requests
        """
        return CrewJoinRequest.select().where(
            CrewJoinRequest.user == user,
            CrewJoinRequest.crew == crew,
            CrewJoinRequest.date
            > datetime.datetime.now()
            - datetime.timedelta(
                hours=Env.CREW_JOIN_REQUEST_COOLDOWN_SAME_CREW_DURATION.get_int()
            ),
        )


CrewJoinRequest.create_table()

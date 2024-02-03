from datetime import datetime

from peewee import *

import resources.Environment as Env
from src.model.BaseModel import BaseModel
from src.model.User import User


class ImpelDownLog(BaseModel):
    """
    Impel Down Log class
    """

    id = PrimaryKeyField()
    user = ForeignKeyField(
        User, backref="impel_down_users", on_delete="CASCADE", on_update="CASCADE"
    )
    sentence_type = CharField(max_length=99, null=True)
    source = CharField(max_length=10, null=True)
    date_time = DateTimeField(default=datetime.now)
    release_date_time = DateTimeField(null=True)
    is_permanent = BooleanField(default=False)
    bounty_action = CharField(max_length=99, null=True)
    reason = CharField(max_length=999, null=True)
    previous_bounty = BigIntegerField(null=True)
    new_bounty = BigIntegerField(null=True)
    message_sent = BooleanField(default=False)
    is_reversed = BooleanField(default=False)
    external_id = IntegerField(null=True)
    bail_amount = BigIntegerField(null=True)
    bail_date = DateTimeField(null=True)
    bail_payer: User | ForeignKeyField = ForeignKeyField(
        User, backref="impel_down_bail_payers", null=True, on_delete="RESTRICT"
    )

    class Meta:
        db_table = "impel_down_log"

    @staticmethod
    def get_current_for_user(user: User):
        """
        Get the current impel down log for the user
        :param user: The user
        :return: The impel down log
        """
        if not user.is_arrested():
            return None

        return (
            ImpelDownLog.select()
            .where(
                (ImpelDownLog.user == user)
                & (ImpelDownLog.is_reversed == False)
                & (
                    (ImpelDownLog.is_permanent == True)
                    | (ImpelDownLog.release_date_time > datetime.now())
                )
                & (ImpelDownLog.bail_date.is_null())
            )
            .first()
        )

    def get_bail(self):
        """
        Get the bail for the user
        :return: The bail
        """

        # Get how many minutes until the release
        minutes = int((self.release_date_time - datetime.now()).total_seconds() / 60)

        if minutes < 0:
            return 0

        return minutes * Env.IMPEL_DOWN_BAIL_PER_MINUTE.get_int()


ImpelDownLog.create_table()

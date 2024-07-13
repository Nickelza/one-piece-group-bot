import datetime

from peewee import *

from src.model.BaseModel import BaseModel
from src.model.Group import Group


class GroupChat(BaseModel):
    """
    Group Chat class
    """

    id: int | PrimaryKeyField = PrimaryKeyField()
    group: Group | ForeignKeyField = ForeignKeyField(
        Group, backref="group_chats", on_delete="CASCADE", on_update="CASCADE"
    )
    tg_topic_id: int | IntegerField = IntegerField(null=True)  # Nullable for general group_chat
    tg_topic_name: str | CharField = CharField(
        null=True
    )  # Only for topics, it's the first name of the topic (even if it's changed)
    last_message_date: datetime.datetime | DateTimeField = DateTimeField(
        default=datetime.datetime.now
    )
    last_error_date: datetime.datetime | DateTimeField = DateTimeField(null=True)
    last_error_message: str | CharField = CharField(null=True)
    is_active: bool | BooleanField = BooleanField(default=True)
    is_muted: bool | BooleanField = BooleanField(default=False)
    auto_delete_duration: int | IntegerField = IntegerField(null=True)  # In minutes

    # Backref
    enabled_disabled_features = None
    enabled_features_pin = None

    class Meta:
        db_table = "group_chat"

    def get_full_name(self):
        """Get the full name of the group chat"""

        #  noinspection PyTypeChecker
        group: Group = self.group

        title = group.tg_group_name
        # Group is forum, add forum name if available
        if group.is_forum and self.tg_topic_name is not None:
            title += " - " + self.tg_topic_name

        return title


GroupChat.create_table()

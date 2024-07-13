from peewee import *

from src.model.BaseModel import BaseModel
from src.model.GroupChat import GroupChat


class GroupChatEnabledDisabledFeature(BaseModel):
    """
    GroupChat Enabled/Disabled Feature class
    """

    id = PrimaryKeyField()
    group_chat = ForeignKeyField(
        GroupChat, backref="enabled_disabled_features", on_delete="CASCADE", on_update="CASCADE"
    )
    feature = SmallIntegerField()

    class Meta:
        db_table = "group_chat_enabled_disabled_feature"


GroupChatEnabledDisabledFeature.create_table()

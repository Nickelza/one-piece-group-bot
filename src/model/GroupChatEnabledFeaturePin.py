from peewee import *

from src.model.BaseModel import BaseModel
from src.model.GroupChat import GroupChat


class GroupChatEnabledFeaturePin(BaseModel):
    """
    GroupChat Enabled Feature Pin class
    """

    group_chat = ForeignKeyField(
        GroupChat, backref="enabled_features_pin", on_delete="CASCADE", on_update="CASCADE"
    )
    feature = SmallIntegerField()

    class Meta:
        db_table = "group_chat_enabled_feature_pin"


GroupChatEnabledFeaturePin.create_table()

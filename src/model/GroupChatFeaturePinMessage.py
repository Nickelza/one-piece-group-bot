from peewee import *

from src.model.BaseModel import BaseModel
from src.model.GroupChat import GroupChat


class GroupChatFeaturePinMessage(BaseModel):
    """
    GroupChat Enabled Feature Pin class
    """

    group_chat = ForeignKeyField(
        GroupChat,
        backref="enabled_features_pin_messages",
        on_delete="CASCADE",
        on_update="CASCADE",
    )
    feature = SmallIntegerField()
    message_id = BigIntegerField()

    class Meta:
        db_table = "group_chat_feature_pin_message"


GroupChatFeaturePinMessage.create_table()

from peewee import *

from src.model.BaseModel import BaseModel
from src.model.GroupChat import GroupChat


class GroupChatDisabledFeature(BaseModel):
    """
    GroupChat Disabled Feature class
    """
    id = PrimaryKeyField()
    group_chat = ForeignKeyField(GroupChat, backref='disabled_features', on_delete='CASCADE', on_update='CASCADE')
    feature = SmallIntegerField()

    class Meta:
        db_table = 'group_chat_disabled_feature'


GroupChatDisabledFeature.create_table()

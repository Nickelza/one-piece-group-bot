from peewee import *

from src.model.BaseModel import BaseModel
from src.model.Group import Group


class GroupDisabledFeature(BaseModel):
    """
    Group Disabled Feature class
    """
    id = PrimaryKeyField()
    group = ForeignKeyField(Group, backref='disabled_features', on_delete='CASCADE', on_update='CASCADE')
    feature = SmallIntegerField()

    class Meta:
        db_table = 'group_disabled_feature'


GroupDisabledFeature.create_table()

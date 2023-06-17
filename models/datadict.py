from models.base import BaseModel
from flask_peewee.db import CharField, IntegerField, DateTimeField


# 通知
class DataDict(BaseModel):
    type = CharField()  # 类型
    key = CharField()  # 键
    value = CharField()  # 值
    comment = CharField()  # 备注
    status = IntegerField(default=0)  # 状态

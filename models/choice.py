from models.base import BaseModel
from flask_peewee.db import CharField, IntegerField, DateTimeField


# 入选池
class Choice(BaseModel):
    code = CharField()  # 编码
    name = CharField()  # 名称
    source = CharField()  # 來源
    strategy = CharField()  # 策略值
    sid = IntegerField()  # 信號ID
    created = DateTimeField()

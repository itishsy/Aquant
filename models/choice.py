from models.base import BaseModel
from flask_peewee.db import CharField, IntegerField, DateTimeField


# 入选池
class Choice(BaseModel):
    code = CharField()  # 编码
    name = CharField()  # 名称
    freq = IntegerField()  # 级别
    dt = DateTimeField()  # 时间
    strategy = CharField()  # 入池策略：uar、drc、hot
    value = CharField()  # 策略值
    status = IntegerField(default=1)  # 状态: 0 失效 1 有效
    created = DateTimeField()
    updated = DateTimeField()

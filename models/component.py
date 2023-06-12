from models.base import BaseModel
from flask_peewee.db import CharField, IntegerField, DateTimeField


# 通知
class Component(BaseModel):
    name = CharField()  # 名称
    clock_time = DateTimeField  # 最近打卡时间
    run_time = DateTimeField  # 最近执行时间
    status = IntegerField(default=0)  # 状态

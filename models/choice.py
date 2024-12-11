from models.base import BaseModel, db
from models.signal import Signal
from flask_peewee.db import CharField, IntegerField, DateTimeField, AutoField, DecimalField
from datetime import datetime


# 入选池
class Choice(BaseModel):
    id = AutoField()
    code = CharField()  # 编码
    name = CharField()  # 名称
    strategy = CharField()  # 策略
    dt = CharField()  # signal.dt
    price = DecimalField()  # 价格
    status = IntegerField(default=1)  # 状态
    created = DateTimeField()
    updated = DateTimeField(null=True)

    class Status:
        DISUSE = 0
        WATCH = 1
        DEAL = 2
        DONE = 3

        @staticmethod
        def all():
            return [(Choice.Status.DISUSE, '弃用'), (Choice.Status.WATCH, '观察'), (Choice.Status.DEAL, '交易'), (Choice.Status.DONE, '剔除')]

        @staticmethod
        def get(key):
            if key == Choice.Status.DISUSE:
                return '弃用'
            if key == Choice.Status.WATCH:
                return '观察'
            if key == Choice.Status.DEAL:
                return '交易'
            if key == Choice.Status.DONE:
                return '剔除'


if __name__ == '__main__':
    db.connect()
    db.create_tables([Choice])

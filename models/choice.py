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
    sid = IntegerField()  # 信號ID
    wid = IntegerField(null=True)  # 信號ID
    freq = CharField(null=True)  # 級別
    dt = CharField(null=True)  # 信號時間
    price = DecimalField(null=True)  # 信号价格
    source = CharField(null=True)  # 來源
    status = IntegerField(default=1)  # 状态
    created = DateTimeField()
    updated = DateTimeField(null=True)

    def add_by_signal(self, sig: Signal):
        if not Choice.select().where(Choice.code == sig.code,
                                     Choice.dt == sig.dt,
                                     Choice.freq == sig.freq).exists():
            self.code = sig.code
            self.name = sig.name
            self.freq = sig.freq
            self.status = Choice.Status.WATCH
            self.dt = sig.dt
            self.sid = sig.id
            self.price = sig.price
            self.strategy = sig.strategy
            self.created = datetime.now()
            self.save()

    class Status:
        DISUSE = 0
        WATCH = 1
        DEAL = 2
        KICK = 3

        @staticmethod
        def all():
            return [(Choice.Status.DISUSE, '弃用'), (Choice.Status.WATCH, '观察'), (Choice.Status.DEAL, '交易'), (Choice.Status.KICK, '剔除')]

        @staticmethod
        def get(key):
            if key == Choice.Status.DISUSE:
                return '弃用'
            if key == Choice.Status.WATCH:
                return '观察'
            if key == Choice.Status.DEAL:
                return '交易'
            if key == Choice.Status.KICK:
                return '剔除'


if __name__ == '__main__':
    db.connect()
    db.create_tables([Choice])

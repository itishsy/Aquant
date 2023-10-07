from models.base import BaseModel, db
from models.signal import Signal
from flask_peewee.db import CharField, IntegerField, DateTimeField, AutoField, DecimalField
from datetime import datetime


# 入选池
class Choice(BaseModel):
    id = AutoField()
    code = CharField()  # 编码
    name = CharField()  # 名称
    source = CharField()  # 來源
    sid = IntegerField()  # 信號ID
    freq = CharField()  # 級別
    dt = CharField()  # 信號時間
    price = DecimalField()  # 信号价格
    strategy = CharField()  # 策略值
    status = IntegerField(default=1)  # 状态
    created = DateTimeField()
    updated = DateTimeField(null=True)

    def add_by_signal(self, sig: Signal):
        self.code = sig.code
        self.name = sig.name
        self.freq = sig.freq
        self.dt = sig.dt
        self.sid = sig.id
        self.price = sig.price
        self.created = datetime.now()
        self.save()


class CHOICE_STATUS:
    DISUSE = 0
    WATCH = 1
    DEAL = 2
    REMOVE = 3

    @staticmethod
    def all():
        return [(CHOICE_STATUS.DISUSE, '弃用'), (CHOICE_STATUS.WATCH, '观察'), (CHOICE_STATUS.DEAL, '交易'), (CHOICE_STATUS.REMOVE, '移除')]

    @staticmethod
    def get(key):
        if key == CHOICE_STATUS.DISUSE:
            return '弃用'
        if key == CHOICE_STATUS.WATCH:
            return '观察'
        if key == CHOICE_STATUS.DEAL:
            return '交易'
        if key == CHOICE_STATUS.REMOVE:
            return '移除'


if __name__ == '__main__':
    db.connect()
    db.create_tables([Choice])

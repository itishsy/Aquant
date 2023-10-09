from dataclasses import dataclass
from models.signal import Signal
from models.choice import Choice
# from sqlalchemy import select, desc, and_, text
from models.base import BaseModel, db
from flask_peewee.db import CharField, AutoField, IntegerField, DateTimeField, DecimalField
# from storage.dba import dba
# from typing import List
from datetime import datetime, timedelta


# 票据
class Ticket(BaseModel):
    id = AutoField()
    code = CharField()  # 编码
    name = CharField()  # 名称
    status = IntegerField(default=0)  # 状态
    strategy = CharField()  # 策略
    cid = IntegerField()  # choice id
    bs_freq = CharField()  # 信號級別
    bs_dt = CharField()  # 信號時間
    bs_price = DecimalField()  # 信號價格
    bs_strength = IntegerField()  # 信號强度
    bp_freq = CharField()  # 買點級別
    bp_dt = CharField()  # 買點時間
    bp_price = DecimalField()  # 買點價格
    hold = IntegerField()  # 持有量
    cost = DecimalField()  # 成本
    created = DateTimeField()
    updated = DateTimeField()

    def add_by_choice(self, cho: Choice, sig: Signal):
        if not Ticket.select().where(Ticket.cid == cho.id).exists():
            self.code = cho.code
            self.name = cho.name
            self.cid = cho.get_id()
            self.strategy = cho.strategy
            self.cid = cho.id
            self.bs_freq = cho.freq
            self.bs_dt = cho.dt
            self.bs_price = cho.price
            self.bp_dt = sig.dt
            self.bp_freq = sig.freq
            self.bp_price = sig.price
            self.created = datetime.now()
            self.save()

    def add_ticket_signal(self, sig: Signal):
        ts = Ticket_Signal()
        ts.tid = self.get_id()
        ts.sid = sig.id
        ts.created = datetime.now()
        ts.save()


class TicketSignal(BaseModel):
    tid = IntegerField()
    sid = IntegerField()
    created = DateTimeField()


class TICKET_STATUS:
    DEAL = 0
    HOLD = 1
    KICK = 2

    @staticmethod
    def all():
        return [(TICKET_STATUS.DEAL, '交易'), (TICKET_STATUS.HOLD, '持有'), (TICKET_STATUS.KICK, '剔除')]

    @staticmethod
    def get(key):
        if key == TICKET_STATUS.DEAL:
            return '交易'
        if key == TICKET_STATUS.HOLD:
            return '持有'
        if key == TICKET_STATUS.KICK:
            return '剔除'


if __name__ == '__main__':
    db.connect()
    db.create_tables([Ticket, Ticket_Signal])

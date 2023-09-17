from dataclasses import dataclass
from models.signal import Signal
from models.choice import Choice
# from sqlalchemy import select, desc, and_, text
from models.base import BaseModel, db
from flask_peewee.db import CharField, BooleanField, IntegerField, DateTimeField, DecimalField
# from storage.dba import dba
# from typing import List
from datetime import datetime, timedelta


# import traceback

#
# @dataclass
# class Ticket2:
#     def __init__(self, code, dt, freq):
#         self.code = code
#         self.dt = dt
#         self.freq = freq
#
#     id: int
#     code: str
#     freq: int
#     dt: str
#     status: int  # 0 观察中， 1 持有 2 清仓 3 弃用
#     b_freq: str  # 可买入级别，如：15+
#     s_freq: str  # 可卖出级别。如：5，15，30
#     cut_point: str  # 止损点
#     created: datetime = datetime.now()
#     updated: datetime = None
#

# 票据
class Ticket(BaseModel):
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

    def add_by_bps(self, bs: Choice, bp: Signal):
        self.code = bs.code
        self.name = bs.name
        self.cid = bs.get_id()
        self.strategy = bs.strategy
        self.cid = bs.id
        self.bs_freq = bs.freq
        self.bs_dt = bs.dt
        self.bs_price = bs.price
        self.bp_dt = bp.dt
        self.bp_freq = bp.freq
        self.bp_price = bp.price
        self.created = datetime.now()
        self.save()

    def add_ticket_signal(self, sig: Signal):
        ts = Ticket_Signal()
        ts.tid = self.get_id()
        ts.sid = sig.id
        ts.created = datetime.now()
        ts.save()


class Ticket_Signal(BaseModel):
    tid = IntegerField()
    sid = IntegerField()
    created = DateTimeField()


class TICKET_STATUS:
    ZERO = 0
    DEAL = 1
    KICK = 2

    @staticmethod
    def all():
        return [(TICKET_STATUS.ZERO, '待定'), (TICKET_STATUS.DEAL, '交易'), (TICKET_STATUS.KICK, '剔除')]

    @staticmethod
    def get(key):
        if key == TICKET_STATUS.ZERO:
            return '待定'
        if key == TICKET_STATUS.DEAL:
            return '交易'
        if key == TICKET_STATUS.KICK:
            return '剔除'


if __name__ == '__main__':
    db.connect()
    db.create_tables([Ticket, Ticket_Signal])

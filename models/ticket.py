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

    def add_by_choice(self, cho: Choice):
        self.code = cho.code
        self.name = cho.name
        self.cid = cho.get_id()
        self.status = TICKET_STATUS.WATCH
        self.strategy = cho.strategy
        self.cid = cho.s_id
        sig = Signal.get_by_id(cho.s_id)
        self.bs_freq = sig.freq
        self.bs_dt = sig.dt
        self.bs_price = sig.price
        self.created = datetime.now()
        self.save()

    def update_bp(self, sig: Signal):
        self.bp_freq = sig.freq
        self.bp_dt = sig.dt
        self.bp_price = sig.price
        self.updated = datetime.now()
        self.save()


class TICKET_STATUS:
    ZERO = 0
    WATCH = 1
    DEAL = 2
    HOLD = 3
    KICK = 4

    @staticmethod
    def all():
        return [(TICKET_STATUS.ZERO, '待定'), (TICKET_STATUS.WATCH, '观察'), (TICKET_STATUS.DEAL, '操作'),
                (TICKET_STATUS.HOLD, '持有'), (TICKET_STATUS.KICK, '剔除')]

    @staticmethod
    def get(key):
        if key == TICKET_STATUS.ZERO:
            return '待定'
        if key == TICKET_STATUS.WATCH:
            return '观察'
        if key == TICKET_STATUS.DEAL:
            return '操作'
        if key == TICKET_STATUS.HOLD:
            return '持有'
        if key == TICKET_STATUS.KICK:
            return '弃用'


#
# def get_ticket(code) -> Signal:
#     session = dba.get_session()
#     sig = session.execute(
#         select(Ticket).where(Ticket.code == code)
#     ).scalar()
#     session.close()
#     return sig

#
# def count_tickets():
#     session = dba.get_session()
#     count = session.query(Ticket).count()
#     session.close()
#     return count

#
# def save_ticket_by_signal(signal: Signal, status):
#     session = dba.get_session()
#     try:
#         tic = get_ticket(signal.code)
#         if tic is None:
#             ticket = Ticket(signal.code, signal.dt, signal.freq)
#             ticket.b_freq = '30,60'
#             ticket.status = 0
#             ticket.created = datetime.now()
#             ticket.updated = datetime.now()
#             session.add(ticket)
#             session.commit()
#         else:
#             mappings = [{'id': tic.id, 'status': status}]
#             session.bulk_update_mappings(Ticket, mappings)
#             session.flush()
#             session.commit()
#         return 1
#     except Exception as ex:
#         traceback.print_exc()
#         session.rollback()
#         return 0

#
# def update_ticket(mappings):
#     session = dba.get_session()
#     try:
#         session.bulk_update_mappings(Ticket, mappings)
#         session.flush()
#         session.commit()
#     except:
#         session.rollback()


if __name__ == '__main__':
    db.connect()
    db.create_tables([Ticket])

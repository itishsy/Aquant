from dataclasses import dataclass
# from models.signal import Signal
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
    cost = DecimalField(default=0.0)  # 成本
    hold = IntegerField(default=0)  # 持有总量
    strategy = CharField()  # 交易策略
    buy = CharField()  # 买入类别
    watch = IntegerField()  # 监控级别
    cut = DecimalField(default=0.0)  # 止损
    clean = IntegerField()  # 剔除级别
    status = IntegerField(default=0)  # 状态 0 观察中， 1 持有 2 清仓 3 弃用
    source = CharField()  # 来源
    created = DateTimeField()
    updated = DateTimeField()


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

from models.base import BaseModel
from flask_peewee.db import CharField, DecimalField, IntegerField, DateTimeField


# from sqlalchemy import select, desc, and_, text
# from storage.dba import dba
# from typing import List
# from datetime import datetime, timedelta


# 信号
class Signal(BaseModel):
    code = CharField()  # 票据
    type = IntegerField()  # 类型： 0 buy 1 sell
    name = CharField()  # 名称
    freq = CharField()  # 信号级别
    dt = CharField()  # 发生时间
    source = CharField()  # 信号源：背离、背驰、量价背离、放量
    status = IntegerField(default=1)  # 状态 0 忽略 1 确认
    price = DecimalField()  # 时价
    notify = IntegerField(default=0)  # 通知 0 未通知， 1 已通知
    created = DateTimeField()
    updated = DateTimeField()

#
# def find_signals(watch=None) -> List[Signal]:
#     session = dba.get_session()
#     if watch is None:
#         clauses = and_(1 == 1)
#     else:
#         clauses = and_(Signal.watch == watch)
#     sgs = session.execute(
#         select(Signal).where(clauses)
#     ).scalars().fetchall()
#     session.close()
#     return sgs

#
# def get_signal(id) -> Signal:
#     session = dba.get_session()
#     sig = session.execute(
#         select(Signal).where(Signal.id == id)
#     ).scalar()
#     session.close()
#     return sig

#
# def count_signals(today=False):
#     session = dba.get_session()
#     if today:
#         dt = datetime.now().strftime('%Y-%m-%d')
#         count = session.query(Signal).filter(Signal.created >= dt).count()
#     else:
#         count = session.query(Signal).count()
#     session.close()
#     return count

#
# def update_signal_watch(ident, watch):
#     session = dba.get_session()
#     try:
#         mappings = [{'id': ident, 'watch': watch}]
#         session.bulk_update_mappings(Signal, mappings)
#         session.flush()
#         session.commit()
#     except:
#         session.rollback()


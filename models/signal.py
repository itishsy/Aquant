from models.base import BaseModel
from flask_peewee.db import CharField, DecimalField, IntegerField, DateTimeField


# from sqlalchemy import select, desc, and_, text
# from storage.dba import dba
# from typing import List
# from datetime import datetime, timedelta


# 信号
class Signal(BaseModel):
    code = CharField()  # 票据
    name = CharField()  # 名称
    freq = CharField()  # 信号级别
    dt = CharField()  # 发生时间
    price = DecimalField()  # 信号价格
    type = IntegerField()  # 信號類別： 0 底背离 1 頂背离
    strength = IntegerField()  # 强度： 0 弱 1 中 2 强
    effect = IntegerField()  # 有效性：0 無效 1 有效 2 破坏
    notify = IntegerField()  # 通知 0 待通知， 1 已通知
    created = DateTimeField()
    updated = DateTimeField()


class SIGNAL_TYPE:
    BOTTOM_DIVERGENCE = 0
    TOP_DIVERGENCE = 1
    TREND_SUPPORT = 2
    PLATFORM_SUPPORT = 3

    def all(self):
        return [(self.BOTTOM_DIVERGENCE, '底背離'), (self.TOP_DIVERGENCE, '頂背離'), (self.TREND_SUPPORT, '趨勢綫支撐'),
                (self.PLATFORM_SUPPORT, '平臺支撐')]

    def get(self, key):
        if key == self.BOTTOM_DIVERGENCE:
            return '底背離'
        if key == self.TOP_DIVERGENCE:
            return '頂背離'
        if key == self.TREND_SUPPORT:
            return '趨勢綫支撐'
        if key == self.PLATFORM_SUPPORT:
            return '平臺支撐'


class SIGNAL_STRENGTH:
    WEAK = 0
    AVERAGE = 1
    STRONG = 2

    def all(self):
        return [(self.WEAK, '弱'), (self.AVERAGE, '中'), (self.STRONG, '強')]

    def get(self, key):
        if key == self.WEAK:
            return '弱'
        if key == self.AVERAGE:
            return '中'
        if key == self.STRONG:
            return '強'

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


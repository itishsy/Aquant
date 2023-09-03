from models.base import BaseModel, db
from flask_peewee.db import CharField, DecimalField, IntegerField, DateTimeField, AutoField


# from sqlalchemy import select, desc, and_, text
# from storage.dba import dba
# from typing import List
# from datetime import datetime, timedelta


# 信号
class Signal(BaseModel):
    id = AutoField()
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

    @staticmethod
    def all():
        return [(SIGNAL_TYPE.BOTTOM_DIVERGENCE, '底背離'),
                (SIGNAL_TYPE.TOP_DIVERGENCE, '頂背離'),
                (SIGNAL_TYPE.TREND_SUPPORT, '趨勢綫支撐'),
                (SIGNAL_TYPE.PLATFORM_SUPPORT, '平臺支撐')]

    @staticmethod
    def get(key):
        if key == SIGNAL_TYPE.BOTTOM_DIVERGENCE:
            return '底背離'
        if key == SIGNAL_TYPE.TOP_DIVERGENCE:
            return '頂背離'
        if key == SIGNAL_TYPE.TREND_SUPPORT:
            return '趨勢綫支撐'
        if key == SIGNAL_TYPE.PLATFORM_SUPPORT:
            return '平臺支撐'


class SIGNAL_STRENGTH:
    WEAK = 0
    AVERAGE = 1
    STRONG = 2

    @staticmethod
    def all():
        return [(SIGNAL_STRENGTH.WEAK, '弱'),
                (SIGNAL_STRENGTH.AVERAGE, '中'),
                (SIGNAL_STRENGTH.STRONG, '強')]

    @staticmethod
    def get(key):
        if key == SIGNAL_STRENGTH.WEAK:
            return '弱'
        if key == SIGNAL_STRENGTH.AVERAGE:
            return '中'
        if key == SIGNAL_STRENGTH.STRONG:
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


if __name__ == '__main__':
    db.connect()
    db.create_tables([Signal])

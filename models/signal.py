from dataclasses import dataclass
from models.base import BaseModel, db
from flask_peewee.db import CharField, BooleanField, IntegerField, DateTimeField
from sqlalchemy import select, desc, and_, text
from storage.dba import dba
from typing import List
from datetime import datetime, timedelta


@dataclass
class Signal2:
    def __init__(self, dt, freq, type, value):
        self.dt = dt
        self.type = type
        self.freq = freq
        self.value = value

    id: int
    code: str
    dt: str
    freq: int
    type: str
    value: int
    watch: int = 0
    created: datetime = datetime.now()


# 信号
class Signal(BaseModel):
    code = CharField()  # 编码
    name = CharField()  # 名称
    freq = IntegerField()  # 主级别
    dt = DateTimeField()  # 时间
    strategy = CharField()  # 策略
    value = CharField()  # 策略值
    tick = IntegerField(default=0)  # 转票据
    status = IntegerField(default=1)  # 状态
    created = DateTimeField()
    updated = DateTimeField()


def find_signals(watch=None) -> List[Signal]:
    session = dba.get_session()
    if watch is None:
        clauses = and_(1 == 1)
    else:
        clauses = and_(Signal.watch == watch)
    sgs = session.execute(
        select(Signal).where(clauses)
    ).scalars().fetchall()
    session.close()
    return sgs


def get_signal(id) -> Signal:
    session = dba.get_session()
    sig = session.execute(
        select(Signal).where(Signal.id == id)
    ).scalar()
    session.close()
    return sig


def count_signals(today=False):
    session = dba.get_session()
    if today:
        dt = datetime.now().strftime('%Y-%m-%d')
        count = session.query(Signal).filter(Signal.created >= dt).count()
    else:
        count = session.query(Signal).count()
    session.close()
    return count


def update_signal_watch(ident, watch):
    session = dba.get_session()
    try:
        mappings = [{'id': ident, 'watch': watch}]
        session.bulk_update_mappings(Signal, mappings)
        session.flush()
        session.commit()
    except:
        session.rollback()


if __name__ == '__main__':
    db.connect()
    db.create_tables([Signal])

from dataclasses import dataclass
from datetime import datetime
from sqlalchemy import select, desc, and_, text
from storage.db import db
from typing import List
from datetime import datetime, timedelta


@dataclass
class Signal:
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



def find_signals(watch=None) -> List[Signal]:
    session = db.get_session(Entity.Signal)
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
    session = db.get_session(Entity.Signal)
    sig = session.execute(
        select(Signal).where(Signal.id == id)
    ).scalar()
    session.close()
    return sig


def count_signals(today=False):
    session = db.get_session(Entity.Signal)
    if today:
        dt = datetime.now().strftime('%Y-%m-%d')
        count = session.query(Signal).filter(Signal.created >= dt).count()
    else:
        count = session.query(Signal).count()
    session.close()
    return count


def update_signal_watch(ident, watch):
    session = db.get_session(Entity.Signal)
    try:
        mappings = [{'id': ident, 'watch': watch}]
        session.bulk_update_mappings(Signal, mappings)
        session.flush()
        session.commit()
    except:
        session.rollback()



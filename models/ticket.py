from decimal import Decimal
from dataclasses import dataclass
from models.signal import Signal
from sqlalchemy import select, desc, and_, text
from storage.db import db
from typing import List
from datetime import datetime, timedelta


@dataclass
class Ticket:
    def __init__(self, code, dt, freq):
        self.code = code
        self.dt = dt
        self.freq = freq

    id: int
    code: str
    freq: int
    dt: str
    status: int  # 0 观察中， 1 持有 2 清仓 3 弃用
    b_freq: str  # 可买入级别，如：15+
    s_freq: str  # 可卖出级别。如：5，15，30
    cut_point: str  # 止损点
    created: datetime = datetime.now()
    updated: datetime = None


def find_tickets() -> List[Ticket]:
    session = db.get_session('ticket')
    clauses = and_(Ticket.status == 1)
    tis = session.execute(
        select(Ticket).where(clauses)
    ).scalars().fetchall()
    session.close()
    return tis


def get_ticket(code) -> Signal:
    session = db.get_session(Entity.Ticket)
    sig = session.execute(
        select(Ticket).where(Ticket.code == code)
    ).scalar()
    session.close()
    return sig


def count_tickets():
    session = db.get_session(Entity.Ticket)
    count = session.query(Ticket).count()
    session.close()
    return count


def save_ticket_by_signal(signal: Signal, status):
    session = db.get_session(Entity.Ticket)
    try:
        tic = get_ticket(signal.code)
        if tic is None:
            ticket = Ticket(signal.code, signal.dt, signal.freq)
            ticket.b_freq = '30,60'
            ticket.status = 0
            ticket.created = datetime.now()
            ticket.updated = datetime.now()
            session.add(ticket)
            session.commit()
        else:
            mappings = [{'id': tic.id, 'status': status}]
            session.bulk_update_mappings(Ticket, mappings)
            session.flush()
            session.commit()
        return 1
    except Exception as ex:
        traceback.print_exc()
        session.rollback()
        return 0


def update_ticket(mappings):
    session = db.get_session(Entity.Ticket)
    try:
        session.bulk_update_mappings(Ticket, mappings)
        session.flush()
        session.commit()
    except:
        session.rollback()

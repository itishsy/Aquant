from decimal import Decimal
from dataclasses import dataclass
from sqlalchemy import select, desc, and_, text
from storage.db import db
from typing import List
from datetime import datetime, timedelta


@dataclass
class Candle:
    def __init__(self, series=None):
        if series is not None:
            for key in series.keys():
                setattr(self, key, series[key])

    id: int
    dt: str
    freq: int
    open: Decimal
    close: Decimal
    high: Decimal
    low: Decimal
    volume: Decimal = None
    turnover: Decimal = None
    ma5: Decimal = None
    ma10: Decimal = None
    ma20: Decimal = None
    ma30: Decimal = None
    mav5: Decimal = None
    ema12: Decimal = None
    ema26: Decimal = None
    dea9: Decimal = None
    mark: int = 0

    def diff(self):
        return self.ema12 - self.ema26

    def bar(self):
        return self.diff() - self.dea9



def find_candles(code, freq, begin='2015-01-01', end=None, limit=10000) -> List[Candle]:
    if begin is None:
        begin = '2015-01-01'
    session = db.get_session(code)
    clauses = and_(Candle.freq == freq, Candle.dt >= begin)
    if end is not None:
        clauses = clauses.__and__(Candle.dt < end)
    cds = session.execute(
        select(Candle).where(clauses).order_by(desc(Candle.dt)).limit(limit)
    ).scalars().fetchall()
    session.close()
    return list(reversed(cds))


def find_stage_candles(code, freq, candle) -> List[Candle]:
    """
    根据一根candle查找所处指定级别的一段candles
    :param code:
    :param freq:
    :param candle:
    :return:
    """
    if freq == candle.freq:
        dt = candle.dt
    else:
        if candle.freq > 100:
            beg = datetime.strptime(candle.dt, '%Y-%m-%d')
        else:
            beg = datetime.strptime(candle.dt, '%Y-%m-%d %H:%M')
        if freq > 100:
            dt = beg.strftime('%Y-%m-%d')
        else:
            dt = beg.strftime('%Y-%m-%d %H:%M')

    session = db.get_session(code)
    clauses = and_(Candle.freq == freq, Candle.dt <= dt)
    cds = []
    pre_candles = session.execute(
        select(Candle).where(clauses).order_by(desc(Candle.dt)).limit(100)
    ).scalars().fetchall()
    for pc in pre_candles:
        if (pc.mark > 0) == (candle.mark > 0):
            cds.insert(0, pc)
        else:
            break
    clauses = and_(Candle.freq == freq, Candle.dt > dt)
    nex_candles = session.execute(
        select(Candle).where(clauses).order_by(Candle.dt).limit(100)
    ).scalars().fetchall()
    for nc in nex_candles:
        if (nc.mark > 0) == (candle.mark > 0):
            cds.append(nc)
        else:
            break
    session.close()
    return cds


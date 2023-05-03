import efinance as ef
from datetime import datetime, timedelta
from entities.candle import Candle
from entities.symbol import Symbol
from decimal import Decimal
from storage.mark import do_macd_mark
from storage.db import db
from sqlalchemy import select, desc, and_, text
from typing import List
from enums.entity import Entity


def fetch_data(code, klt, begin='20100101'):
    session = db.get_session(code)
    l_candle = session.execute(
        select(Candle).where(Candle.klt == klt).order_by(desc('id')).limit(1)
    ).scalar()
    if l_candle is not None:
        dtime = None
        if l_candle.dt.find(':') > 0:
            dtime = datetime.strptime(l_candle.dt, '%Y-%m-%d %H:%M') + timedelta(days=1)
        else:
            dtime = datetime.strptime(l_candle.dt, '%Y-%m-%d') + timedelta(days=1)
        begin = dtime.strftime('%Y%m%d')

    df = ef.stock.get_quote_history(code, klt=klt, beg=begin)
    df.columns = ['name', 'code', 'dt', 'open', 'close', 'high', 'low', 'volume', 'amount', 'zf', 'zdf', 'zde',
                  'turnover']
    df.drop(['name', 'code', 'zf', 'zdf', 'zde'], axis=1, inplace=True)

    candles = []
    for i, row in df.iterrows():
        row['klt'] = klt
        c = Candle(row)
        if i == 0:
            if l_candle is not None and l_candle.ema12 is not None:
                c.ema5 = l_candle.ema5 * Decimal(4 / 6) + Decimal(c.close) * Decimal(2 / 6)
                c.ema12 = l_candle.ema12 * Decimal(11 / 13) + Decimal(c.close) * Decimal(2 / 13)
                c.ema26 = l_candle.ema26 * Decimal(25 / 27) + Decimal(c.close) * Decimal(2 / 27)
                c.dea4 = l_candle.dea4 * Decimal(3 / 5) + Decimal(c.ema5 - c.ema12) * Decimal(2 / 5)
                c.dea9 = l_candle.dea9 * Decimal(8 / 10) + Decimal(c.ema12 - c.ema26) * Decimal(2 / 10)
            else:
                c.ema5 = Decimal(c.close)
                c.ema12 = Decimal(c.close)
                c.ema26 = Decimal(c.close)
                c.dea4 = Decimal(0)
                c.dea9 = Decimal(0)
        else:
            c.ema5 = candles[i - 1].ema5 * Decimal(4 / 6) + Decimal(c.close) * Decimal(2 / 6)
            c.ema12 = candles[i - 1].ema12 * Decimal(11 / 13) + Decimal(c.close) * Decimal(2 / 13)
            c.ema26 = candles[i - 1].ema26 * Decimal(25 / 27) + Decimal(c.close) * Decimal(2 / 27)
            c.dea4 = candles[i - 1].dea4 * Decimal(3 / 5) + Decimal(c.ema5 - c.ema12) * Decimal(2 / 5)
            c.dea9 = candles[i - 1].dea9 * Decimal(8 / 10) + Decimal(c.ema12 - c.ema26) * Decimal(2 / 10)
        candles.append(c)
    session.add_all(do_macd_mark(candles))
    session.commit()


def fetch_symbols():
    session = db.get_session(Entity.Symbol)
    df = ef.stock.get_realtime_quotes(['沪A', '深A', 'ETF'])
    df = df.iloc[:, 0:2]
    df.columns = ['code', 'name']
    df = df[df['name'].str.contains('ST') == False]
    symbols = []
    for i, row in df.iterrows():
        s = Symbol(row)
        s.status = 1
        symbols.append(s)
    session.add_all(symbols)
    session.commit()


def fetch_all():
    sbs = find_active_symbols()
    for sb in sbs:
        fetch_data(sb.code, 102)
        fetch_data(sb.code, 101)
        fetch_data(sb.code, 60)
        fetch_data(sb.code, 30)


def find_active_symbols() -> List[Symbol]:
    session = db.get_session(Entity.Symbol)
    sbs = session.execute(
        select(Symbol).where(and_(Symbol.status == 1))
    ).scalars().fetchall()
    return sbs


def find_candles(code, klt, begin='2010-01-01', end=None, limit=10000) -> List[Candle]:
    session = db.get_session(code)
    clauses = and_(Candle.klt == klt, Candle.dt >= begin)
    if end is not None:
        clauses = clauses.__and__(Candle.dt < end)
    cds = session.execute(
        select(Candle).where(clauses).order_by(desc(Candle.dt)).limit(limit)
    ).scalars().fetchall()
    return list(reversed(cds))


if __name__ == '__main__':
    # fetch_symbols()
    # fetch_data('300223', 30)
    candles = find_candles('300223', 101, begin='2023-01-01', limit=100)
    for c in candles:
        print(c)
    # fetch_all()

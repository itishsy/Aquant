import efinance as ef
from datetime import datetime, timedelta
from entities.candle import Candle
from decimal import Decimal
from storage.mark import do_macd_mark
from storage.db import db
from sqlalchemy import select, desc, and_, text
from typing import List


def fetch_data(code, klt, begin='20100101'):
    session = db.get_session(code)
    l_candle = session.execute(
        select(Candle).where(Candle.klt == klt).order_by(desc('id')).limit(1)
    ).scalar()
    if l_candle is not None:
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


def find_candles(code, klt, begin='2010-01-01', end=None, limit=10000) -> List[Candle]:
    session = db.get_session(code)
    clauses = and_(Candle.klt == klt, Candle.dt >= begin)
    if end is not None:
        clauses = clauses.__and__(Candle.dt < end)
    cds = session.execute(
        select(Candle).where(clauses).limit(limit)
    ).scalars().fetchall()
    return cds


if __name__ == '__main__':
    fetch_data('300223', 30)
    candles = find_candles('300223', 30, begin='2023-01-01', limit=100)
    print(len(candles))

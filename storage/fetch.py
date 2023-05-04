import efinance as ef
from datetime import datetime, timedelta
from entities.candle import Candle
from entities.symbol import Symbol
from decimal import Decimal
from storage.db import db
from sqlalchemy import select, desc, and_
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


def mark(code, klt):
    session = db.get_session(code)
    unmark_candles = session.execute(
        select(Candle).where(Candle.klt == klt, Candle.macd_mark == None)
    ).scalars().fetchall()
    mark_candles = do_macd_mark(unmark_candles)
    mappings = []
    for cand in mark_candles:
        dic = {'id': cand.id, 'macd_mark': cand.macd_mark}
        mappings.append(dic)
    session.bulk_update_mappings(Candle, mappings)
    session.flush()
    session.commit()


def do_macd_mark(candles: List[Candle]) -> List[Candle]:
    size = len(candles)

    for c in candles:
        c.macd_mark = 1 if c.bar() > 0 else -1

    for i in range(2, size):
        c_2 = candles[i - 2]
        c_1 = candles[i - 1]
        c_0 = candles[i]
        if c_2.macd_mark == c_1.macd_mark == c_0.macd_mark == -1:
            if c_2.diff() > c_1.diff() < c_0.diff():
                c_1.macd_mark = -3
        if c_2.macd_mark == c_1.macd_mark == c_0.macd_mark == 1:
            if c_2.diff() < c_1.diff() > c_0.diff():
                c_1.macd_mark = 3

    i = 2
    while i < size:
        if abs(candles[i].macd_mark) < 3:
            i = i + 1
            continue

        if candles[i].macd_mark == -3:
            min_diff = candles[i].diff()
            j = i + 1
            while j < size:
                if candles[j].macd_mark > 0:
                    break
                if candles[j].macd_mark == -3:
                    if min_diff > candles[j].diff():
                        candles[i].macd_mark = -2
                        min_diff = candles[j].diff()
                    else:
                        candles[j].macd_mark = -2
                j = j + 1
            i = j

        if candles[i].macd_mark == 3:
            max_diff = candles[i].diff()
            j = i + 1
            while j < size:
                if candles[j].macd_mark < 0:
                    break
                if candles[j].macd_mark == 3:
                    if max_diff < candles[j].diff():
                        candles[i].macd_mark = 2
                        max_diff = candles[j].diff()
                    else:
                        candles[j].macd_mark = 2
                j = j + 1
            i = j
    return candles


if __name__ == '__main__':
    # fetch_symbols()
    # mark('300223', 101)
    # fetch_data('300223', 30)
    fetch_all()

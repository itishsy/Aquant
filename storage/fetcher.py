import efinance as ef
from datetime import datetime, timedelta
from entities.candle import Candle
from entities.symbol import Symbol
from decimal import Decimal
from storage.db import db
from sqlalchemy import select, desc, delete, and_
from storage.marker import mark
from enums.entity import Entity
from storage.db import find_active_symbols
from typing import List
import logging
import time


def fetch_and_save(code, klt, begin='2015-01-01'):
    session = db.get_session(code)
    l_candle = session.execute(
        select(Candle).where(Candle.klt == klt).order_by(desc('id')).limit(1)
    ).scalar()
    if l_candle is not None:
        if l_candle.dt.find(':') > 0:
            sdt = datetime.strptime(l_candle.dt, '%Y-%m-%d %H:%M')
        else:
            sdt = datetime.strptime(l_candle.dt, '%Y-%m-%d')
        session.execute(delete(Candle).where(and_(Candle.klt == klt,Candle.dt >= sdt.strftime('%Y-%m-%d'))))
        session.commit()
        begin = sdt.strftime('%Y%m%d')
    candles = fetch_data(code, klt, begin, l_candle=l_candle)
    session.add_all(mark(candles))
    session.commit()


def need_upset(sdt):
    now = datetime.now()
    if sdt.month == now.month and sdt.day == now.day and now.hour < 15:
        return True
    return False


def fetch_data(code, klt, begin, l_candle=None) -> List[Candle]:
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
                c.ema12 = l_candle.ema12 * Decimal(11 / 13) + Decimal(c.close) * Decimal(2 / 13)
                c.ema26 = l_candle.ema26 * Decimal(25 / 27) + Decimal(c.close) * Decimal(2 / 27)
                c.dea9 = l_candle.dea9 * Decimal(8 / 10) + Decimal(c.ema12 - c.ema26) * Decimal(2 / 10)
            else:
                c.ema12 = Decimal(c.close)
                c.ema26 = Decimal(c.close)
                c.dea9 = Decimal(0)
        else:
            if klt == 101:
                c.ma5 = get_ma(candles, 5, c.close)
                c.ma10 = get_ma(candles, 10, c.close)
                c.ma20 = get_ma(candles, 20, c.close)
                c.ma30 = get_ma(candles, 30, c.close)
                c.mav5 = get_ma(candles, 5, c.volume, att='volume')
            c.ema12 = candles[i - 1].ema12 * Decimal(11 / 13) + Decimal(c.close) * Decimal(2 / 13)
            c.ema26 = candles[i - 1].ema26 * Decimal(25 / 27) + Decimal(c.close) * Decimal(2 / 27)
            c.dea9 = candles[i - 1].dea9 * Decimal(8 / 10) + Decimal(c.ema12 - c.ema26) * Decimal(2 / 10)
        candles.append(c)
    return mark(candles)


def get_ma(candles: List[Candle], seq, val=None, att='close'):
    res = val
    ss = 0
    siz = len(candles)
    if val is None:
        res = 0.0
        sta = siz - seq
    else:
        ss = val
        sta = siz - seq - 1
    if siz > seq:
        cds = candles[sta:]
        for cd in cds:
            ss = ss + eval('cd.' + att)
        res = Decimal(ss / seq)
    return res


def fetch_symbols():
    session = db.get_session(Entity.Symbol)
    sbs = session.query(Symbol).all()
    if len(sbs) == 0:
        df = ef.stock.get_realtime_quotes(['沪A', '深A', 'ETF'])
        df = df.iloc[:, 0:2]
        df.columns = ['code', 'name']
        df = df[df['name'].str.contains('ST') is False]
        symbols = []
        for i, row in df.iterrows():
            s = Symbol(row)
            s.status = 1
            symbols.append(s)
        session.add_all(symbols)
        session.commit()


def fetch_all(kls=None):
    if kls is None:
        kls = [102, 101, 60, 30, 15]
    sbs = find_active_symbols()
    for sb in sbs:
        try:
            for klt in kls:
                fetch_and_save(sb.code, klt)
        except:
            logging.error('{} error'.format(sb.code))


def fetch_daily():
    while True:
        try:
            now = datetime.now()
            if now.weekday() < 5 and now.hour == 16 and now.minute < 3:
                print("start fetching.", now)
                fetch_all()
                print('fetch all done!')
        except Exception as e:
            print(e)
        finally:
            time.sleep(60)


if __name__ == '__main__':
    # fetch_daily()
    # fetch_symbols()
    # df = ef.stock.get_quote_history('300133', klt=15, beg='20230511')
    # print('===============df')
    # print(df)
    fetch_and_save('300133', 15, begin='2023-05-11')
    # fetch_all()

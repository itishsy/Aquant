import efinance as ef
from datetime import datetime
from storage.candle import Candle
from storage.symbol import Symbol
from decimal import Decimal
from storage.dba import dba, freqs, find_candles
from sqlalchemy import select, desc, delete, and_
from storage.marker import remark
from enums.entity import Entity
from storage.dba import find_active_symbols
from typing import List
import logging
import time


def fetch_and_save(code, freq, begin='2015-01-01'):
    session = dba.get_session(code)
    a_candles = session.execute(
        select(Candle).where(Candle.freq == freq).order_by(desc('id')).limit(100)
    ).scalars().fetchall()
    if len(a_candles) == 0:
        return
    l_candle = a_candles[0]
    if l_candle is not None:
        if l_candle.dt.find(':') > 0:
            sdt = datetime.strptime(l_candle.dt, '%Y-%m-%d %H:%M')
        else:
            sdt = datetime.strptime(l_candle.dt, '%Y-%m-%d')
        session.execute(delete(Candle).where(and_(Candle.freq == freq, Candle.dt >= sdt.strftime('%Y-%m-%d'))))
        session.commit()
        begin = sdt.strftime('%Y%m%d')
    l_candle = session.execute(
        select(Candle).where(Candle.freq == freq).order_by(desc('id')).limit(1)
    ).scalar()
    candles = fetch_data(code, freq, begin, l_candle=l_candle)
    session.add_all(candles)
    session.commit()
    remark(code, freq, beg=a_candles[-1].dt)


def need_upset(sdt):
    now = datetime.now()
    if sdt.month == now.month and sdt.day == now.day and now.hour < 15:
        return True
    return False


def fetch_data(code, freq, begin, l_candle=None) -> List[Candle]:
    df = ef.stock.get_quote_history(code, klt=freq, beg=begin)
    df.columns = ['name', 'code', 'dt', 'open', 'close', 'high', 'low', 'volume', 'amount', 'zf', 'zdf', 'zde',
                  'turnover']
    df.drop(['name', 'code', 'zf', 'zdf', 'zde'], axis=1, inplace=True)
    candles = []
    for i, row in df.iterrows():
        row['freq'] = freq
        c = Candle(row)
        if freq == 101:
            cs = find_candles(code, freq, limit=100)
            c.ma5 = get_ma(cs, 5, c.close)
            c.ma10 = get_ma(cs, 10, c.close)
            c.ma20 = get_ma(cs, 20, c.close)
            c.ma30 = get_ma(cs, 30, c.close)
            c.mav5 = get_ma(cs, 5, c.volume, att='volume')
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
            c.ema12 = candles[i - 1].ema12 * Decimal(11 / 13) + Decimal(c.close) * Decimal(2 / 13)
            c.ema26 = candles[i - 1].ema26 * Decimal(25 / 27) + Decimal(c.close) * Decimal(2 / 27)
            c.dea9 = candles[i - 1].dea9 * Decimal(8 / 10) + Decimal(c.ema12 - c.ema26) * Decimal(2 / 10)
        candles.append(c)
    return candles


def get_ma(candles: List[Candle], seq, val=None, att='close'):
    ss = 0
    siz = len(candles)
    if val is None:
        res = Decimal(0.0)
        sta = siz - seq
    else:
        res = Decimal(val)
        ss = Decimal(val)
        sta = siz - seq + 1
    if siz > seq:
        cds = candles[sta:]
        for cd in cds:
            ev = eval('cd.' + att)
            ss = Decimal(ss) + Decimal(ev)
        res = Decimal(ss / seq)
    return res


def fetch_symbols():
    session = dba.get_session()
    sbs = session.query(Symbol).all()
    if len(sbs) == 0:
        df = ef.stock.get_realtime_quotes(['沪A', '深A', 'ETF'])
        df = df.iloc[:, 0:2]
        df.columns = ['code', 'name']
        # df = df[df['name'].str.contains('ST') is False]
        symbols = []
        for i, row in df.iterrows():
            s = Symbol(row)
            s.status = 1
            symbols.append(s)
        session.add_all(symbols)
        session.commit()


def fetch_all(freq=None):
    start_time = datetime.now()
    ks = []
    if freq is not None:
        ks.append(freq)
    else:
        ks = freqs
    sbs = find_active_symbols()
    count = 0
    for sb in sbs:
        try:
            for k in ks:
                fetch_and_save(sb.code, k)
            print('[{}] {} fetch candles [{}] done!'.format(datetime.now(), count, sb.code))
            count = count + 1
        except Exception as ex:
            print('fetch candles [{}] error!'.format(sb.code))
            logging.error('fetch candles [{}] error!'.format(sb.code), ex)
    print('[{}] fetch all done! elapsed time:'.format(datetime.now(), datetime.now() - start_time))


def fetch_daily():
    print('[{}] daily fetch working'.format(datetime.now()))
    while True:
        now = datetime.now()
        try:
            if now.weekday() < 5 and (
                    (now.hour == 11 and now.minute == 35) or (now.hour == 15 and now.minute == 10)):
                fetch_all()
                print("==============用時：{}=================".format(datetime.now() - now))
        except Exception as e:
            print(e)
        finally:
            if now.minute == 1:
                print('[{}] daily fetch working'.format(now))
            time.sleep(60)


if __name__ == '__main__':
    fetch_daily()
    # fetch_all(freq=101)

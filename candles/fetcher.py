import efinance as ef
from datetime import datetime, timedelta
from candles.candle import Candle
from models.symbol import Symbol
from decimal import Decimal
from candles.storage import dba, find_candles
from common.config import Config
from sqlalchemy import select, desc, delete, and_, text
from candles.marker import remark
from candles.storage import clean_data
from typing import List
from common.utils import dt_format
from models.component import Component
import logging
import time
import pandas as pd
import math


def get_last_candle(code, freq, l_candle: Candle):
    session = dba.get_session(code)
    begin = '2015-01-01'
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
    return l_candle, begin


def fetch_and_save(code, freq, begin=None):
    session = dba.get_session(code)
    a_candles = session.execute(
        select(Candle).where(Candle.freq == freq).order_by(desc('id')).limit(100)
    ).scalars().fetchall()
    if len(a_candles) == 0:
        candles = fetch_data(code, freq, begin)
        session.add_all(candles)
        session.commit()
        update_ma(code)
        remark(code, freq)
    else:
        l_candle, begin = get_last_candle(code, freq, a_candles[0])
        beg = a_candles[-1].dt
        candles = fetch_data(code, freq, begin, l_candle=l_candle)
        session.add_all(candles)
        session.commit()
        update_ma(code)
        remark(code, freq, beg=beg)


def double_merge(candles):
    single_candles = candles.iloc[::2]  # 获取单行
    double_candles = candles.iloc[1::2]  # 获取双行
    single_candles.reset_index(drop=True, inplace=True)
    double_candles.reset_index(drop=True, inplace=True)
    for index, row in double_candles.iterrows():
        single_row = single_candles.iloc[index]
        row.open = single_row.open
        if row.high < single_row.high:
            row.high = single_row.high
        if row.low > single_row.low:
            row.low = single_row.low
    return double_candles


def fetch_data(code, freq, begin, l_candle=None) -> List[Candle]:
    d_flag = False
    if freq == 10:
        d_flag = True
        freq = 5
    if begin:
        beg = dt_format(begin, '%Y%m%d')
    else:
        beg = cal_fetch_beg(freq)

    df = ef.stock.get_quote_history(code, klt=freq, beg=beg)
    df.columns = ['name', 'code', 'dt', 'open', 'close', 'high', 'low', 'volume', 'amount', 'zf', 'zdf', 'zde',
                  'turnover']
    df.drop(['name', 'code', 'zf', 'zdf', 'zde'], axis=1, inplace=True)
    if d_flag:
        df = double_merge(df)
    # if freq == 101:
    #     df['ma5'] = df['close'].rolling(5).mean()
    #     df['ma10'] = df['close'].rolling(10).mean()
    #     df['ma20'] = df['close'].rolling(20).mean()
    #     df['ma30'] = df['close'].rolling(30).mean()
    #     df['ma60'] = df['close'].rolling(60).mean()
    #     df.fillna(0)

    candles = []
    for i, row in df.iterrows():
        if d_flag:
            row['freq'] = 10
        else:
            row['freq'] = freq
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


def update_ma(code):
    sen = dba.get_session(code)
    query = text("select * from `{}` where freq=101 order by dt desc limit 120;".format(code))
    result_proxy = sen.execute(query)
    # select(Candle).where(and_(Candle.freq == 101)).order_by(desc(Candle.dt)).limit(120)
    # )
    df = pd.DataFrame(result_proxy.fetchall(), columns=result_proxy.keys())
    df = df[::-1]
    df['ma5'] = df['close'].rolling(5).mean()
    df['ma10'] = df['close'].rolling(10).mean()
    df['ma20'] = df['close'].rolling(20).mean()
    df['ma30'] = df['close'].rolling(30).mean()
    df['ma60'] = df['close'].rolling(60).mean()
    for index, row in df.iterrows():
        if isinstance(row['ma60'], float) and math.isnan(row['ma60']):
            continue
        update_sql = text("update `{}` set ma5={},ma10={},ma20={},ma30={},ma60={} where freq=101 and dt='{}'"
                          .format(code, row['ma5'], row['ma10'], row['ma20'], row['ma30'], row['ma60'], row['dt']))
        sen.execute(update_sql)
    sen.close()


def fetch_all(freq=None, clean=False):
    start_time = datetime.now()
    ks = []
    if freq is not None:
        if isinstance(freq, list):
            ks = freq
        else:
            ks.append(freq)
    else:
        ks = Config.FREQ
    sbs = Symbol.actives()
    count = 0
    for sb in sbs:
        try:
            print('[{}] {} fetch candles [{}] start!'.format(datetime.now(), count, sb.code))
            if clean:
                clean_data(sb.code)
            for k in ks:
                fetch_and_save(sb.code, k)
            print('[{}] {} fetch candles [{}] done!'.format(datetime.now(), count, sb.code))
            count = count + 1
        except Exception as ex:
            print('fetch candles [{}] error!'.format(sb.code), ex)
    print('[{}] fetch all done! elapsed time:'.format(datetime.now(), datetime.now() - start_time))


def cal_fetch_beg(freq):
    now = datetime.now()
    beg = ''
    if freq == 102:
        beg = (now - timedelta(1000)).strftime('%Y%m%d')
    if freq == 101:
        beg = (now - timedelta(200)).strftime('%Y%m%d')
    elif freq == 120:
        beg = (now - timedelta(100)).strftime('%Y%m%d')
    elif freq == 60:
        beg = (now - timedelta(50)).strftime('%Y%m%d')
    elif freq == 30:
        beg = (now - timedelta(25)).strftime('%Y%m%d')
    elif freq == 15:
        beg = (now - timedelta(13)).strftime('%Y%m%d')
    elif freq == 5:
        beg = (now - timedelta(4)).strftime('%Y%m%d')
    return beg


def fetch_daily():
    print('[{}] fetcher start ...'.format(datetime.now()))
    while True:
        now = datetime.now()
        try:
            Component.update(clock_time=now).where(Component.name == 'fetcher').execute()
            if now.weekday() < 5 and now.hour > 15:
                fet = Component.get(Component.name == 'fetcher')
                fet_time = fet.run_end  # datetime.p(fet.run_time, '%Y-%m-%d %H:%M:%S')
                if fet_time.day < now.day or fet_time.hour < 15:
                    fetch_all()
                    print("==============用時：{}=================".format(datetime.now() - now))
        except Exception as e:
            print(e)
        finally:
            time.sleep(60 * 30)


if __name__ == '__main__':
    # fetch_daily()
    # fetch_all(clean=True)
    # update_ma('600876')
    idx = 0
    for symbol in Symbol.actives():
        idx = idx + 1
        print('update candle', symbol.code, idx)
        session = dba.get_session(symbol.code)
        session.execute(delete(Candle).where(Candle.freq == 101))
        session.commit()
        fetch_and_save(symbol.code, 101)

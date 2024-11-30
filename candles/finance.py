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
import signals.utils as utl
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


def double_merge(candles, freq):
    single_candles = candles.iloc[::2]  # 获取单行
    double_candles = candles.iloc[1::2]  # 获取双行
    single_candles.reset_index(drop=True, inplace=True)
    double_candles.reset_index(drop=True, inplace=True)
    for index, row in double_candles.iterrows():
        single_row = single_candles.iloc[index]
        row.open = single_row.open
        row.freq = freq
        if row.high < single_row.high:
            row.high = single_row.high
        if row.low > single_row.low:
            row.low = single_row.low
    return double_candles


def fetch_data(code, freq, begin=None, l_candle=None) -> List[Candle]:
    if begin:
        beg = dt_format(begin, '%Y%m%d')
    else:
        beg = cal_fetch_beg(freq)

    if freq == 10:
        df = ef.stock.get_quote_history(code, klt=5, beg=beg)
        df = double_merge(df, freq)
    else:
        df = ef.stock.get_quote_history(code, klt=freq, beg=beg)

    df.columns = ['name', 'code', 'dt', 'open', 'close', 'high', 'low', 'volume', 'amount', 'zf', 'zdf', 'zde',
                  'turnover']
    df.drop(['name', 'code', 'zf', 'zdf', 'zde'], axis=1, inplace=True)

    candles = []
    for i, row in df.iterrows():
        c = Candle(row)
        c.freq = freq
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
    query_dt = text("select dt from `{}` where freq=101 and ma60 is not null order by dt desc limit 1;".format(code))
    dt = sen.execute(query_dt).scalar_one_or_none()
    if dt == datetime.now().strftime('%Y-%m-%d'):
        return
    query = text("select * from `{}` where freq=101 order by dt desc limit 120;".format(code))
    result_proxy = sen.execute(query)
    df = pd.DataFrame(result_proxy.fetchall(), columns=result_proxy.keys())
    df = df[::-1]
    df['ma5'] = df['close'].rolling(5).mean()
    df['ma10'] = df['close'].rolling(10).mean()
    df['ma20'] = df['close'].rolling(20).mean()
    df['ma30'] = df['close'].rolling(30).mean()
    df['ma60'] = df['close'].rolling(60).mean()
    if dt is not None:
        df = df[df['dt'] > dt]
    for index, row in df.iterrows():
        if isinstance(row['ma60'], float) and not math.isnan(row['ma60']):
            update_sql = text("update `{}` set ma5={},ma10={},ma20={},ma30={},ma60={} where freq=101 and dt='{}'"
                              .format(code, round(row['ma5'], 4), round(row['ma10'], 4), round(row['ma20'], 4),
                                      round(row['ma30'], 4), round(row['ma60'], 4), row['dt']))
            sen.execute(update_sql)
            sen.commit()
    sen.close()


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
    elif freq == 10:
        beg = (now - timedelta(10)).strftime('%Y%m%d')
    elif freq == 5:
        beg = (now - timedelta(5)).strftime('%Y%m%d')
    return beg


if __name__ == '__main__':
    # fetch_daily()
    # fetch_all(freq=103, clean=True)
    # update_ma('000030')
    idx = 0
    for symbol in Symbol.actives():
        idx = idx + 1
        # print('find_candle diver_bottom:', symbol.code, idx)
        candles1 = find_candles(symbol.code, freq=103)
        signals = []
        tbs = utl.get_top_bottom(candles1)
        size = len(tbs)
        for i in range(2, size):
            c_2 = tbs[i - 2]
            c_1 = tbs[i - 1]
            c_0 = tbs[i]
            if c_2.mark == -3 and c_1.mark == 3 and c_0.mark == -3 and c_2.diff() < 0 and c_1.diff() < 0 and c_0.diff() < 0:
                is_cross = True
                if i + 1 == size:
                    cs = utl.get_section(candles1, c_0.dt, candles1[-1].dt)
                    if utl.has_cross(cs) != 1:
                        is_cross = False
                if is_cross:
                    down_stage1 = utl.get_stage(candles1, c_2.dt)
                    down_stage2 = utl.get_stage(candles1, c_0.dt)
                    if utl.has_trend(down_stage1) > -2 and utl.has_trend(down_stage2) > -2:
                        low1 = utl.get_lowest(down_stage1)
                        low2 = utl.get_lowest(down_stage2)
                        lowest = utl.get_lowest(utl.get_section(candles1, low1.dt))
                        if c_2.diff() < c_0.diff() and low1.low > low2.low == lowest.low and low2.dt > '2024-01-01':
                            print(idx, 'search single=', symbol.code, symbol.name, low2.dt, low2.low)

        # session = dba.get_session(symbol.code)
        # session.execute(delete(Candle).where(Candle.freq == 101))
        # session.commit()
        # fetch_and_save(symbol.code, 101)

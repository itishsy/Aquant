from typing import List
from decimal import Decimal

from candles.candle import Candle
import signals.utils as utl
from candles.storage import find_candles
from signals.divergence import diver_bottom, diver_top, driver_bottom_plus
from candles.finance import fetch_data
from candles.marker import mark


def choices(code, size):
    candles = find_candles(code)
    if len(candles) == 100:
        return candles[-size:]


# 是否高位放量
def is_top_volume(candles: List[Candle], pre_ratio=0.8, nxt_ratio=0.9):
    highest = utl.get_highest(candles)
    if highest.dt == candles[-1].dt:
        return False
    c_size = len(candles)
    v_highest = utl.get_highest_volume(candles)
    if highest.dt == v_highest.dt:
        idx = 0
        for c in candles:
            if 0 < idx < (c_size-1) \
                    and highest.dt == c.dt \
                    and candles[idx - 1].volume / c.volume <= pre_ratio \
                    and candles[idx + 1].volume / c.volume <= nxt_ratio:
                return True
            idx = idx + 1
    return False


# 是否活跃的
def is_active(candles: List[Candle], zhang_ting=0.097, zhang_ting_size=1, high_turnover=3.5, high_turnover_size=2):
    ht_counter = 0  # 高换手
    zt_counter = 0  # 大涨幅
    close = 0
    for c in candles:
        if c.turnover > high_turnover:
            ht_counter = ht_counter + 1
        if close > 0 and (c.close - close) > 0 and (c.close - close) / close >= zhang_ting:
            zt_counter = zt_counter + 1
        close = c.close
    if ht_counter >= high_turnover_size and zt_counter >= zhang_ting_size:
        return True
    return False


# 是否顶背离
def is_top_divergence(code, freq, limit=None):
    cds = find_candles(code, freq)
    dts = diver_top(cds)
    if len(dts) > 0:
        sig = dts[-1]
        if limit is None or len(utl.get_section(cds, sig.dt)) <= limit:
            return True
    return False


# 是否在ma线之上
def is_beyond_ma(candles: List[Candle], ma_level, ma_ratio=1):
    beyond_ma_counter = 0
    for c in candles:
        ma_val = eval('c.ma' + str(ma_level))
        if c.close > ma_val:
            beyond_ma_counter = beyond_ma_counter + 1
    if beyond_ma_counter/len(candles) >= ma_ratio:
        return True
    return False


# 是否大A形态
def is_big_a(candles: List[Candle], down_ratio=0.618):
    highest = utl.get_highest(candles)
    lowest = utl.get_lowest(candles)
    lower_sec = utl.get_section(candles, highest.dt)
    if len(lower_sec) < len(candles)/2:
        lower = utl.get_lowest(lower_sec)
        if (highest.high - Decimal(lower.low)) / (highest.high - Decimal(lowest.low)) >= down_ratio:
            return True
    return False


def driver_bottom_signal(code, freq, limit):
    if freq > 15:
        cds = find_candles(code, freq=freq)
        dbs = diver_bottom(cds)
    else:
        cds = fetch_data(code, freq)
        cds = mark(cds)
        dbs = diver_bottom(cds)
    if len(dbs) > 0:
        sig = driver_bottom_plus(dbs[-1], cds)
        if sig and len(utl.get_section(cds, sig.dt)) <= limit:
            sig.code = code
            sig.type = 'diver-bottom'
            return sig


def cal_limit(freq, day):
    return day*240/freq

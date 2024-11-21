from candles.storage import find_candles
import signals.utils as utl
from signals.divergence import diver_bottom, diver_top
import candles.fetcher as fet
import candles.marker as mar
from models.signal import Signal
from candles.fetcher import fetch_data
from candles.marker import mark


"""
Buy point of divergence during the adjustment of the upward trend
"""


class MA20:

    @staticmethod
    def search(code):
        candles = find_candles(code)
        size = len(candles)

        # 至少100根
        if size < 100:
            return

        # 在ma上线占比
        lcs = candles[-30:]
        below_close_count = 0
        beyond_ma5_ma10_count = 0
        for c in lcs:
            if c.ma20 > c.close:
                below_close_count = below_close_count + 1
            if c.ma20 >= c.ma5 or c.ma20 >= c.ma10:
                beyond_ma5_ma10_count = beyond_ma5_ma10_count + 1
        if below_close_count > 2 or beyond_ma5_ma10_count > 1:
            return

        # 调整幅度不可过大（最近M根最高最低与当前收盘价比较）
        highest = utl.get_highest(lcs)
        # lowest = utl.get_lowest(lcs)
        # stage_lowest = utl.get_lowest(utl.get_stage(candles, candles[-1].dt))
        # if (highest.high - candles[-1].close) / (highest.high - lowest.low) < 0.618:
        #     return

        # 不可出现量价背离（最高点的那根：阴线或长上影线，收盘不是最高，成交量最大，且远高于平均成高量的）
        v_highest = utl.get_highest_volume(lcs)
        c_highest = utl.get_highest_close(lcs)
        if v_highest.dt == highest.dt and c_highest.dt != highest.dt and highest.close < highest.open:
            bts = utl.get_between(candles, c_highest.dt, 5, 10)
            avg = utl.get_average_volume(bts)
            if avg/highest.volume < 0.6:
                return

        # 不可出现顶背离
        dts = diver_top(candles)
        if len(dts) > 0:
            return

        # 出现次级别底背离
        cds = find_candles(code, freq=30)
        dbs = diver_bottom(cds)
        if len(dbs) == 0:
            cds = fetch_data(code, 15)
            cds = mark(cds)
            dbs = diver_bottom(cds)

        if len(dbs) > 0:
            sig = dbs[-1]
            sec = utl.get_section(cds, sig.dt, candles[-1].dt)
            sec_lowest = utl.get_lowest(sec)
            if sec_lowest.dt == sig.dt:
                return sig

    @staticmethod
    def watch(code, t=0):
        cds = fetch_data(code, 5)
        cds = mark(cds)
        if t <= 0:
            dbs = diver_bottom(cds)
            if len(dbs) > 0:
                sig = dbs[-1]
                sec = utl.get_section(cds, sig.dt, cds[-1].dt)
                sec_lowest = utl.get_lowest(sec)
                if sec_lowest.dt == sig.dt:
                    return sig
        if t >= 0:
            dbs = diver_top(cds)
            if len(dbs) > 0:
                sig = dbs[-1]
                sec = utl.get_section(cds, sig.dt, cds[-1].dt)
                sec_highest = utl.get_highest(sec)
                if sec_highest.dt == sig.dt:
                    return sig


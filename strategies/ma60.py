from candles.storage import find_candles
import signals.utils as utl
from signals.divergence import diver_bottom, diver_top, driver_bottom_plus
from candles.finance import fetch_data
from candles.marker import mark
from decimal import Decimal


"""
Buy point of divergence during the adjustment of the upward trend

"""



class MA60:

    @staticmethod
    def search(code):
        candles = find_candles(code)
        size = len(candles)

        # 至少100根
        if size < 100:
            return

        # 在ma上线占比
        last_30 = candles[-30:]
        below_close_count = 0
        beyond_ma10_ma20_count = 0
        for c in last_30:
            if c.ma60 > c.close:
                below_close_count = below_close_count + 1
            if c.ma60 >= c.ma10 or c.ma60 >= c.ma20:
                beyond_ma10_ma20_count = beyond_ma10_ma20_count + 1
        if below_close_count > 2 or beyond_ma10_ma20_count > 1:
            return

        # 活跃度不足
        turnover_size = 0
        big_up = 0
        close = 0
        for c in last_30:
            if c.turnover < 2:
                turnover_size = turnover_size + 1
            if close > 0 and c.close / close > 1.08:
                big_up = big_up + 1
            close = c.close
        if turnover_size > 3 or big_up < 2:
            return

        # 出现顶背离
        dts = diver_top(candles)
        if len(dts) > 0:
            return
        candles_120 = find_candles(code, freq=120)
        dts = diver_top(candles_120)
        if len(dts) > 0:
            return
        candles_60 = find_candles(code, freq=60)
        dts = diver_top(candles_60)
        if len(dts) > 0:
            return

        # 高位放量
        highest = utl.get_highest(last_30)
        v_highest = utl.get_highest_volume(last_30)
        if highest.dt == v_highest.dt:
            idx = 0
            for c in last_30:
                if 0 < idx < 19 and highest.dt == c.dt and last_30[idx - 1].volume / c.volume < 0.8 and last_30[idx + 1].volume / c.volume < 0.9:
                    return
                idx = idx + 1

        # 大A形态
        lowest = utl.get_lowest(last_30)
        lower_sec = utl.get_section(last_30, highest.dt)
        if len(lower_sec) < 8:
            lower = utl.get_lowest(lower_sec)
            if (highest.high - Decimal(lower.low)) / (highest.high - Decimal(lowest.low)) > 0.5:
                return

        # 15/30min底背离
        cds = find_candles(code, freq=60)
        dbs = diver_bottom(cds)
        if len(dbs) > 0:
            sig = driver_bottom_plus(dbs[-1], cds)
            if sig:
                sig.code = code
                return sig

        cds = fetch_data(code, 30)
        cds = mark(cds)
        dbs = diver_bottom(cds)
        if len(dbs) > 0:
            sig = driver_bottom_plus(dbs[-1], cds)
            if sig:
                sig.code = code
                return sig


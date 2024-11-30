from candles.storage import find_candles
import signals.utils as utl
from signals.divergence import diver_bottom, diver_top
from candles.finance import fetch_data
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
        last_20 = candles[-20:]
        below_close_count = 0
        beyond_ma5_ma10_count = 0
        for c in last_20:
            if c.ma20 > c.close:
                below_close_count = below_close_count + 1
            if c.ma20 >= c.ma5 or c.ma20 >= c.ma10:
                beyond_ma5_ma10_count = beyond_ma5_ma10_count + 1
        if below_close_count > 2 or beyond_ma5_ma10_count > 1:
            return

        # 活跃度不足
        turnover_size = 0
        big_up = 0
        close = 0
        for c in last_20:
            if c.turnover < 2:
                turnover_size = turnover_size + 1
            if close > 0 and c.close / close > 1.08:
                big_up = big_up + 1
            close = c.close
        if turnover_size > 3 or big_up < 3:
            return

        # 出现顶背离
        dts = diver_top(candles)
        if len(dts) > 0:
            return
        candles_60 = find_candles(code, freq=60)
        dts = diver_top(candles_60)
        if len(dts) > 0:
            return

        # 高位放量
        # highest = utl.get_highest(last_20)
        # v_highest = utl.get_highest_volume(last_20)
        # if highest.dt == v_highest.dt:
        #     idx = 0
        #     for c in last_20:
        #         if 0 < idx < 19 and highest.dt == c.dt and last_20[idx - 1].volume < c.volume > last_20[idx + 1].volume:
        #             return
        #         idx = idx + 1

        # 出现15/30min底背离
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

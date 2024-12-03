from candles.storage import find_candles
import signals.utils as utl
from signals.divergence import diver_bottom, diver_top, driver_bottom_plus
from candles.finance import fetch_data
from candles.marker import mark
from decimal import Decimal


"""
Buy point of divergence during the adjustment of the upward trend

"""



class MA10:

    @staticmethod
    def search(code):
        candles = find_candles(code)
        size = len(candles)

        # 至少100根
        if size < 100:
            return

        # 在ma上线占比
        last_10 = candles[-10:]
        below_close_count = 0
        for c in last_10:
            if c.ma5 > c.close and c.ma5 > c.ma10:
                below_close_count = below_close_count + 1
        if below_close_count > 1:
            return

        # 活跃度不足
        turnover_size = 0
        big_up = 0
        close = 0
        for c in last_10:
            if c.turnover < 2:
                turnover_size = turnover_size + 1
            if close > 0 and c.close / close > 1.06:
                big_up = big_up + 1
            close = c.close
        if turnover_size > 1 or big_up < 2:
            return

        # 出现顶背离
        candles_30 = find_candles(code, freq=30)
        dts = diver_top(candles_30)
        if len(dts) > 0:
            return

        # 高位放量
        highest = utl.get_highest(last_10)
        v_highest = utl.get_highest_volume(last_10)
        if highest.dt == v_highest.dt:
            idx = 0
            for c in last_10:
                if 0 < idx < 9 and highest.dt == c.dt and last_10[idx - 1].volume / c.volume < 0.8 and last_10[idx + 1].volume / c.volume < 0.9:
                    return
                idx = idx + 1

        cds = fetch_data(code, 5)
        cds = mark(cds)
        dbs = diver_bottom(cds)
        if len(dbs) > 0:
            sig = driver_bottom_plus(dbs[-1], cds)
            if sig:
                sig.code = code
                return sig


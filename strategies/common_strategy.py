from candles.storage import find_candles
from signals.divergence import diver_top, diver_bottom
from candles.fetcher import fetch_data
from candles.marker import mark
from datetime import datetime

"""
Common filter
"""


class CommonStrategy:

    @staticmethod
    def filter(code):
        candles = find_candles(code)
        size = len(candles)

        # 至少100根
        if size < 100:
            return

        # 换手不足

        t_size = 30
        turnover_size = 0
        for i in range(t_size):
            if candles[size-i-1].turnover > 0.8:
                turnover_size = turnover_size + 1

        if turnover_size < 15:
            return

        # 不可出现日线顶背离
        dts = diver_top(candles)
        if len(dts) > 0:
            return

        return candles

    @staticmethod
    def watch(code, freq):
        candles = fetch_data(code, freq)
        last_candle = candles[-1]
        if last_candle.dt < datetime.now().strftime("%Y-%m-%d 00:00:01"):
            return

        candles = mark(candles)
        dbs = diver_bottom(candles)
        if len(dbs) > 0:
            return dbs[-1]
        dts = diver_top(candles)
        if len(dts) > 0:
            return dts[-1]

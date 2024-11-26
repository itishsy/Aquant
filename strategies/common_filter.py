from candles.storage import find_candles
from signals.divergence import diver_top


"""
Common filter
"""


class Common:

    @staticmethod
    def candles(code):
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


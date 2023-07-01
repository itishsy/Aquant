from strategies.strategy import register_strategy, Strategy
from storage.dba import find_candles
import signals.utils as utl
from signals.divergence import diver_bottom, diver_top
from storage.candle import Candle
from typing import List
from decimal import Decimal


@register_strategy
class UAB(Strategy):

    def search(self, candles: List[Candle]):
        size = len(candles)
        cur = candles[-1]

        # 当前一段处在主体上方（最高-当前阶段最低）/（最高-最低）> 618
        highest = utl.get_highest(candles).high
        lowest = utl.get_lowest(candles).low
        cur_stage = utl.get_stage(candles, cur.dt)
        cur_lowest = utl.get_lowest(cur_stage)
        if (highest - cur_lowest) / (highest - lowest) < 0.618:
            return

        # 主体部分在零轴上方
        ups = 0
        for c in candles:
            if c.diff() > 0:
                ups = ups + 1
        if ups / size < 0.618:
            return

        # 不可出现顶背离
        dts = diver_top(candles)
        if len(dts) > 0:
            return

        for freq in self.child_freq():
            xcs = find_candles(self.code, freq, begin=highest.dt)
            dbs = diver_bottom(xcs)
            if len(dbs) == 0:
                continue
            sig = dbs[-1]
            sig.source = self.__class__.__name__
            sig.value = self.freq
            sig.code = self.code
            self.signals.append(sig)

    def deal(self, tick):
        pass

from strategies.strategy import register_strategy, Strategy
from candles.storage import find_candles
import signals.utils as utl
from signals.divergence import diver_bottom, diver_top
from candles.candle import Candle
from typing import List
from decimal import Decimal


@register_strategy
class UAR(Strategy):

    def search(self, candles: List[Candle]):

        # QC001
        ups = 0
        size = len(candles)
        for c in candles:
            if c.diff() > 0:
                ups = ups + 1
        if ups / size < 0.618:
            return

        # QC002
        dts = diver_top(candles)
        if len(dts) > 0:
            return

        highest = utl.get_highest(candles)
        lowest = utl.get_lowest(candles)
        a_stage = utl.get_stage(candles, highest.dt)
        a_lowest = utl.get_lowest(a_stage)
        # QC003
        if Decimal(highest.high - a_lowest.low) > Decimal(highest.high - lowest.low) * Decimal(0.618):
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

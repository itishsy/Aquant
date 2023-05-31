from strategies.strategy import register_strategy, Strategy
from storage.dba import find_candles
from signals.divergence import diver_bottom, diver_top
from storage.candle import Candle
from typing import List
from datetime import datetime


@register_strategy
class MAR(Strategy):

    def search(self, candles: List[Candle]):
        """ ma线上的买点
        最近连续30日站在30均线上面,出现30/15级别reverse买点
        :param candles:
        :return:
        """

        if candles[-1].close < candles[-1].ma30:
            return

        i = len(candles) - 30
        while i < len(candles):
            if candles[i].ma30 is None or candles[i].close < candles[i].ma30:
                return
            i = i + 1

        sis = diver_top(candles)
        if len(sis) > 0:
            return

        sdt = candles[-30].dt
        ss = []
        for freq in self.child_freq():
            css = find_candles(self.code, freq, begin=sdt)
            cds = diver_bottom(css)
            for cs in cds:
                cs.strategy=self.__class__.__name__,
                cs.value=self.freq
                cs.code = self.code
                self.signals.append(cs)

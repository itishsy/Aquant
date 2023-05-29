from strategies.strategy import register_strategy, Strategy
from storage.db import find_candles
from entities.signal import Signal
from signals.divergence import diver_bottom, diver_top


@register_strategy
class MAR(Strategy):

    def search(self, code):
        """ ma线上的买点
        最近连续30日站在30均线上面,出现30/15级别reverse买点
        :param code:
        :return:
        """

        candles = find_candles(code, self.freq, begin=self.begin, limit=self.limit)
        if len(candles) < self.limit:
            return

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
            css = find_candles(code, freq, begin=sdt)
            cds = diver_bottom(css)
            for cd in cds:
                s = Signal(dt=cd.dt, freq=self.freq, type=self.__class__.__name__, value=cd.freq)
                s.code = code
                ss.append(s)
        self.upset_signals(ss)

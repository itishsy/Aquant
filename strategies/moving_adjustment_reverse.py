from strategies.strategy import register_strategy, Strategy
from storage.db import find_candles, freqs
from storage.fetcher import fetch_data
import signals.signals as sig


@register_strategy
class MAR(Strategy):

    def search(self, code):
        """ ma线上的买点
        最近连续30日站在30均线上面,出现30/15级别reverse买点
        :param code:
        :return:
        """

        candles = find_candles(code, self.freq, begin=self.begin, limit=self.limit)
        if len(candles) == 0 or len(candles) < 30:
            return

        if candles[-1].close < candles[-1].ma30:
            return

        i = len(candles) - 30
        while i < len(candles):
            if candles[i].ma30 is None or candles[i].close < candles[i].ma30:
                return
            i = i + 1

        sis = sig.divergence(candles, is_top=True)
        if len(sis) > 0:
            return

        sdt = candles[-30].dt
        for kl in self.child_freq():
            css = find_candles(code, kl, begin=sdt)
            self.append_signals(code, css)

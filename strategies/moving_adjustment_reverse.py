from strategies.strategy import register_strategy, Strategy
from storage.db import find_candles, freqs
from storage.fetcher import fetch_data
import signals.signals as sig


@register_strategy
class UAR(Strategy):

    def search(self, code):
        """ ma线上的买点
        1. 连续20/30日站在ma20/30均线上面,
        2. 最后一个3以下出现30/15级别reverse买点
        3. 3_-3_3未出现日级或60级别顶背离
        :param code:
        :return:
        """

        candles = find_candles(code, self.freq, begin=self.begin, limit=self.limit)
        if len(candles) == 0 or len(candles) < 30:
            return

        i = len(candles) - 30
        while i > 1:
            if candles[i].mark == 3:
                s_high = sig.get_stage(candles, candles[i].dt)
                highest = sig.get_highest(s_high)
                sdt = highest.dt

        for kl in self.child_freq():
            if kl not in freqs:
                css = fetch_data(code, kl , begin=sdt)
            else:
                css = find_candles(code, kl, begin=sdt)
            self.append_signals(code, css)

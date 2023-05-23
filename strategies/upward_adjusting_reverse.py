from strategies.strategy import register_strategy, Strategy
from storage.db import find_candles, freqs
from storage.fetcher import fetch_data
import signals.signals as sig


@register_strategy
class UAR(Strategy):

    def search(self, code):
        """ 向上趋势调整策略
        1. 前一次的上叉发生在0轴之上
        2. 调整回落的幅度不能超过上涨幅度的黄金分割线
        3. 调整过程中，出现次某级别的背驰买点
        :param code:
        """
        candles = find_candles(code, self.freq, begin=self.begin, limit=self.limit)
        if len(candles) == 0:
            return

        # 最后一根在0轴上方且macd向下调整
        c_last = candles[-1]
        if c_last.bar() > 0 or c_last.diff() < 0 or c_last.dea9 < 0:
            return

        sdt = None
        dea = None
        highest=None
        lowest=None
        i = len(candles) - 1
        while i > 1:
            if candles[i].mark == 3:
                sdt = candles[i].dt
                s_high = sig.get_stage(candles, sdt)
                highest = sig.get_highest(s_high)

            if candles[i - 1].mark < 0 < candles[i].mark:
                # 前一个金叉发生在0轴上
                if candles[i - 1].dea9 < 0:
                    return
                else:
                    dea = candles[i - 1].dea9
                    s_low = sig.get_stage(candles,candles[i-1].dt)
                    lowest = sig.get_lowest(s_low)
                    break
            i = i - 1

        if sdt is None or lowest is None:
            return

        s_cur = sig.get_stage(candles, c_last.dt)
        a_lowest = sig.get_lowest(s_cur)
        if (highest.high - a_lowest.low)/(highest.high - lowest.low) > 0.5:
            return

        # 调整下来的慢线低于上涨启动的快线
        if dea is None or c_last.dea9 < dea:
            return

        for kl in self.child_freq():
            if kl not in freqs:
                css = fetch_data(code, kl , begin=sdt)
            else:
                css = find_candles(code, kl, begin=sdt)
            self.append_signals(code, css)

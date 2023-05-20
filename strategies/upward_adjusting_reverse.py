from strategies.strategy import register_strategy, Strategy
from storage.db import find_candles


@register_strategy
class UAR(Strategy):

    def search(self, code):
        """ 向上趋势调整策略
        1. 前一次的上叉发生在0轴之上
        2. 调整回落的幅度不能超过上涨幅度的黄金分割线
        3. 调整过程中，出现次某级别的背驰买点
        :param code:
        """
        candles = find_candles(code, self.klt, begin=self.begin, limit=self.limit)
        if len(candles) == 0:
            return

        # 最后一根在0轴上方且macd向下调整
        c_last = candles[-1]
        if c_last.bar() > 0 or c_last.diff() < 0 or c_last.dea9 < 0:
            return

        sdt = None
        diff = None
        i = len(candles) - 1
        while i > 1:
            if candles[i].mark == 3:
                sdt = candles[i].dt

            if candles[i - 1].mark < 0 < candles[i - 1].mark:
                # 前一个金叉发生在0轴上
                if candles[i - 1].diff() < 0:
                    return
                else:
                    diff = candles[i - 1].diff()
                    break
            i = i - 1

        # 调整下来的慢线低于上涨启动的快线
        if c_last.dea9 < diff:
            return

        if sdt is None:
            return

        for kl in self.child_klt():
            ccs = find_candles(code, kl, begin=sdt)
            self.fetch_signals(code, ccs)

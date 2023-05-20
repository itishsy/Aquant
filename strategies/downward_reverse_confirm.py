from strategies.strategy import register_strategy, Strategy
from storage.db import find_stage_candles, find_candles
import signals.signals as sig


@register_strategy
class DRC(Strategy):
    def search(self, code):
        """ 下跌趋势反转策略
        满足以下条件：
        1. 大级别最近的快慢线交叉发生在0轴上方,50%以上diff在0轴上方
        2. 本级别发生底背离
        3. 反弹后回落向下确认，快线不破慢线，发生次某级别的一买。
        :param code:
        """
        candles = find_candles(code, self.klt, begin=self.begin, limit=self.limit)
        if len(candles) < self.limit:
            return

        sis = sig.divergence(candles)
        if len(sis) == 0:
            return

        # 获取最后一个
        si = sis[-1]

        # 判断父級別的一段是否符合
        psc = find_stage_candles(code, self.parent_klt(), sig.get_candle(candles, si.dt))
        for sc in psc[:len(psc) // 2]:
            if sc.diff() < 0 or sc.dea9 < 0:
                return

        # 查询C段(确认段)的起始位置（底背离信号－3后第一个mart=3右边的dt）
        flag = False
        flag_3 = False
        sdt = None
        lowest = None
        for c in candles:
            if flag_3:
                sdt = c.dt
            if c.dt == si.dt:
                flag = True
                lowest = c.low
            if flag and c.mark == 3:
                flag_3 = True
                flag = False

        if sdt is None:
            return

        # C段(3,-3)不可连续击穿慢线。
        i = 2
        sts = sig.get_stage(candles, sdt)
        edt = None
        while i < len(sts):
            if sts[i - 1].bar() < 0 and sts[i].bar() < 0:
                return []
            # 最后一个拐点时间
            if (sts[i - 2].bar() > sts[i - 1].bar() < sts[i].bar()) and (
                    sts[i - 2].low > sts[i - 1].low < sts[i].low) and lowest < sts[i - 1].low:
                edt = sts[i].dt
            i = i + 1

        if edt is None:
            return

        # C段子级别出现的背离，是信号
        for kl in self.child_klt():
            ccs = find_candles(code, kl, begin=sdt, end=edt)
            self.append_signals(code, ccs)

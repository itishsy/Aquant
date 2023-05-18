from signals.strategy import register_strategy, Strategy, reverse_signals
from entities.candle import Candle
from entities.signal import Signal
from typing import List
from storage.db import find_candles
import signals.signals as sig


@register_strategy
class UAR(Strategy):

    def search_signal(self, candles: List[Candle]) -> List[Signal]:
        """ 向上趋势调整出现次级别买点
        1. 前一次上叉在0轴上，到后一个下叉上涨幅度超过20%
        2. 调整回落的幅度不能超过上涨幅度的黄金分割线
        3. 调整过程中，出现次某级别的背驰买点
        :param candles:
        :return:
        """
        signals = []
        mark_candles = []
        for cd in candles:
            if abs(cd.mark) == 3:
                mark_candles.append(cd)
        m_last = mark_candles[-1]
        if m_last.mark != -3 or m_last.diff() < 0 or m_last.dea9 < 0 or m_last.bar() < 0:
            return signals
        up_state = sig.get_stage(candles, m_last.dt)
        sdt = None
        for c in up_state:
            if c.diff() < 0 or c.dea9 < 0 or c.bar() < 0:
                return signals
            if sdt is None:
                sdt = c.dt
        kls = self.get_child_klt()
        for kl in kls:
            cds = find_candles(self.code, kl, begin=sdt)
            sis = sig.deviates(cds)
            if len(sis) > 0:
                for si in sis:
                    signals.append(Signal(si.dt, type=self.__class__.__name__, klt=self.klt, value=kl))

        return signals


if __name__ == '__main__':
    pass

from strategies import register_strategy, Strategy, reverse_signals
from entities.candle import Candle
from entities.signal import Signal
from typing import List
from storage.db import find_candles


@register_strategy
class RGA(Strategy):

    def search_signal(self, candles: List[Candle]) -> List[Signal]:
        """ 二次金叉信号
        满足以下条件：
        1. 前一次金叉到二次金叉前，均在0轴上.
        2. 调整回落的幅度不能超过上涨幅度的黄金分割线
        3. 调整过程中，出现次某级别的背离买点
        :param candles:
        :return:
        """

        mark_candles = []
        for cd in candles:
            if abs(cd.mark) == 3:
                mark_candles.append(cd)
        m_size = len(mark_candles)
        i = 2
        signals = []
        while i < m_size:
            c_3 = mark_candles[i - 2]
            c_2 = mark_candles[i - 1]
            c_1 = mark_candles[i]
            # mark段为-3_3_-3，均在零轴上方，
            if c_3.mark == -3 and c_2.mark == 3 and c_1.mark == -3:
                if is_above(c_3) and is_above(c_2) and is_above(c_1):
                    if (c_2.high - c_1.low) / (c_2.high - c_3.low) > 0.5:
                        for klt in [15, 30, 60]:
                            c_candles = find_candles(self.code, klt, begin=c_3.dt)
                            sis = reverse_signals(c_candles)
                            for si in sis:
                                if c_1.dt > si.dt > c_2.dt and si.value == -3:
                                    si.klt = klt
                                    si.type = self.__class__.__name__
                                    signals.append(si)
            i = i + 1
        return signals


def is_above(candle: Candle):
    # 是否在0轴上方
    if candle.diff() > 0 and candle.dea9 > 0:
        return True
    else:
        return False


if __name__ == '__main__':
    pass

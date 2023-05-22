from entities.candle import Candle
from entities.signal import Signal
from typing import List
from strategies import register_strategy, Strategy, reverse_signals
from storage.db import find_candles


@register_strategy
class Rising(Strategy):

    def search_signal(self, candles: List[Candle]) -> List[Signal]:
        """
        1. 连续20/30日站在ma20/30均线上面,
        2. 最后一个3以下出现30/15级别reverse买点
        3. 3_-3_3未出现日级或60级别顶背离
        :param candles:
        :return:
        """
        size = len(candles)
        signals = []
        if size > 30:
            i = size - 20
            j = size - 30
            flag_20 = True
            flag_30 = True
            while i < size:
                if candles[i].ma20 is not None and candles[i].high < candles[i].ma20:
                    flag_20 = False
                    break
                i = i + 1
            if flag_20 is False:
                while j < size:
                    if candles[j].ma30 is not None and candles[j].high < candles[j].ma30:
                        flag_30 = False
                        break
                    j = j + 1
            if flag_20 or flag_30:
                mark_candles = []
                for cd in candles:
                    if abs(cd.mark) == 3:
                        mark_candles.append(cd)
                m_size = len(mark_candles)
                i = 2
                while i < m_size:
                    c_2 = mark_candles[i - 1]
                    c_1 = mark_candles[i]
                    # (c_2.mark == 3 and c_1.mark == -3) or
                    if i == m_size - 1 and c_1.mark == 3:
                        for freq in [15, 30]:
                            beg = c_1.dt # c_2.dt if i < m_size - 1 else c_1.dt
                            c_candles = find_candles(self.code, freq, begin=beg)
                            sis = reverse_signals(c_candles)
                            for si in sis:
                                if si.dt > beg and si.value == -3:
                                    si.freq = freq
                                    si.type = 'rising {} reverse'.format(20 if flag_20 else 30)
                                    signals.append(si)
                    i = i + 1
        return signals



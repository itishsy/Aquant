from entities.candle import Candle
from entities.signal import Signal
from typing import List
from signals.strategy import register_strategy, Strategy, reverse_signals, factory
from storage.fetcher import fetch_data


@register_strategy
class BottomConfirm(Strategy):
    def search_signal(self, candles: List[Candle]) -> List[Signal]:
        sis = reverse_signals(candles)
        signals = []
        if len(sis) > 0:
            i = 0
            s = 0
            s_flag = False
            c_flag = False
            while i < len(candles):
                if s < len(sis) and candles[i].dt == sis[s].dt:
                    s_flag = True
                    s = s + 1
                if s_flag and i > 1 and candles[i - 1].bar() < 0 < candles[i].bar():
                    c_flag = True
                    s_flag = False
                if c_flag:
                    if candles[i].bar() < 0:
                        c_flag = False
                    else:
                        c_2 = candles[i - 2]
                        c_1 = candles[i - 1]
                        c_0 = candles[i]
                        if (c_2.bar() > c_1.bar() < c_0.bar()) and (c_2.low > c_1.low < c_0.low):
                            signals.append(Signal(dt=c_0.dt, type=self.__class__.__name__, value=c_0.mark))
                            c_flag = False
                i = i + 1
        return signals


if __name__ == '__main__':
    st = factory['BottomConfirm']()
    cs = fetch_data('603658', '60', '20230101')
    ss = st.search_signal(cs)
    for s1 in ss:
        print('【signal】 dt={}, value={}'.format(s1.dt, s1.value))

from entities.candle import Candle
from entities.signal import Signal
from typing import List
from signals.strategy import register_strategy, Strategy


@register_strategy
class Rising(Strategy):
    def search_signal(self, candles: List[Candle]) -> List[Signal]:
        size = len(candles)
        signals = []
        if size > 20:
            i = size - 20
            j = size - 10
            k = size - 5
            flag_ma20 = True
            flag_ma10 = True
            flag_ma5 = True
            while i < size:
                if candles[i].close < candles[i].ma20:
                    flag_ma20 = False
                    break
                i = i + 1
            if flag_ma20:
                signals.append(Signal(dt=candles[size - 1].dt, type=Strategy.rising, value=i))
            else:
                while j < size:
                    if candles[j].close < candles[j].ma10:
                        flag_ma10 = False
                        break
                    j = j + 1
                if flag_ma10:
                    signals.append(Signal(dt=candles[size - 1].dt, type=Strategy.rising, value=j))
                else:
                    while k < size:
                        if candles[k].close < candles[k].ma5:
                            flag_ma5 = False
                            break
                        k = k + 1
                    if flag_ma5:
                        signals.append(Signal(dt=candles[size - 1].dt, type=Strategy.rising, value=k))
        return signals

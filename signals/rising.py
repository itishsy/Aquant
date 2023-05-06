from entities.candle import Candle
from entities.signal import Signal
from typing import List
from signals.strategy import register_strategy, Strategy


@register_strategy
class Rising(Strategy):
    def search_signal(self, candles: List[Candle]) -> List[Signal]:
        size = len(candles)
        signals = []
        if size > 26:
            i = size - 26
            flag = True
            while i < size:
                if candles[i].close < candles[i].ema26:
                    flag = False
                    break
            if flag:
                signals.append(Signal(dt=candles[size - 1].dt, type=Strategy.reverse, value=candles[size - 1].mark))
        return signals
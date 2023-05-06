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
            f_26 = True
            while i < size:
                if candles[i].close < candles[i].ema26:
                    f_26 = False
                    break
                i = i + 1
            j = size - 12
            if f_26:
                signals.append(Signal(dt=candles[size - 1].dt, type=Strategy.rising, value=26))
            f_12 = True
            while j < size:
                if candles[j].close < candles[j].ema12:
                    f_12 = False
                    break
                j = j + 1
            if f_12:
                signals.append(Signal(dt=candles[size - 1].dt, type=Strategy.rising, value=12))
        return signals
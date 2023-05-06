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
            j = size - 12
            k = size - 5
            ema_26 = True
            ema_12 = True
            ema_5 = True
            while i < size:
                if candles[i].close < candles[i].ema26:
                    ema_26 = False
                    break
                i = i + 1
            if ema_26:
                signals.append(Signal(dt=candles[size - 1].dt, type=Strategy.rising, value=26))
            else:
                while j < size:
                    if candles[j].close < candles[j].ema12:
                        ema_12 = False
                        break
                    j = j + 1
                if ema_12:
                    signals.append(Signal(dt=candles[size - 1].dt, type=Strategy.rising, value=12))
                else:
                    while k < size:
                        if candles[k].close < candles[k].ema5:
                            ema_5 = False
                            break
                        k = k + 1
                    if ema_5:
                        signals.append(Signal(dt=candles[size - 1].dt, type=Strategy.rising, value=5))

        return signals
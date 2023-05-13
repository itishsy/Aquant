from entities.candle import Candle
from entities.signal import Signal
from typing import List
from signals.strategy import register_strategy, Strategy, reverse_signals


@register_strategy
class Reverse(Strategy):
    def search_signal(self, candles: List[Candle]) -> List[Signal]:
        return reverse_signals(candles)



if __name__ == '__main__':
    pass
    # re = Reverse()
    # search_all()

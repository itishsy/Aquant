from signals.strategy import register_strategy, Strategy
from entities.candle import Candle
from entities.signal import Signal
from typing import List
from storage.db import find_candles


@register_strategy
class GoldCrossFirst(Strategy):

    def search_signal(self, candles: List[Candle]) -> List[Signal]:
        """
        一次金叉信号

        :param candles:
        :return:
        """
        pass


def is_balance(candle: Candle):
    dc = abs(candle.diff() / candle.close)
    if abs(dc) < 0.01:
        return True
    else:
        return False


def is_above(candle: Candle):
    # 是否在0轴上方
    if candle.diff() > 0 and candle.dea9 > 0:
        return True
    else:
        return False


def is_gold_cross(c1: Candle, c2: Candle):
    # 是否在0轴上方的金叉
    if is_above(c1) and is_above(c2) and (c1.bar() < 0) and (c2.bar() > 0):
        return True
    else:
        return False


def is_dead_cross(c1: Candle, c2: Candle):
    # 是否在0轴上方的死叉
    if is_above(c1) and is_above(c2) and (c1.bar() > 0) and (c2.bar() < 0):
        return True
    else:
        return False


if __name__ == '__main__':
    pass

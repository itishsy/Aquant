from entities.candle import Candle
from entities.signal import Signal
from typing import List
# from signals.strategy import register_strategy, Strategy


# @register_strategy
# class Reverse(Strategy):
#     def search_signal(self, candles: List[Candle]) -> List[Signal]:
#         return search_reverse(candles)


def search_reverse(candles: List[Candle]) -> List[Signal]:
    mark_candles = []
    for cd in candles:
        if abs(cd.mark) == 3:
            mark_candles.append(cd)
    size = len(mark_candles)
    signals = []
    for i in range(2, size):
        c_2 = mark_candles[i - 2]
        c_1 = mark_candles[i - 1]
        c_0 = mark_candles[i]
        if c_2.mark == -3 and c_1.mark == 3 and c_0.mark == -3 and c_2.diff() < 0 and c_1.diff() < 0 and c_0.diff() < 0:
            low2 = find_lowest(candles, c_2.dt)
            low0 = find_lowest(candles, c_0.dt)
            if c_2.diff() < c_0.diff() and low2 > low0:
                signals.append(Signal(dt=c_0.dt, type='reverse', value=c_0.mark))
        if c_2.mark == 3 and c_1.mark == -3 and c_0.mark == 3 and c_2.diff() > 0 and c_1.diff() > 0 and c_0.diff() > 0:
            high2 = find_highest(candles, c_2.dt)
            high0 = find_highest(candles, c_0.dt)
            if c_2.diff() > c_0.diff() and high2 < high0:
                signals.append(Signal(dt=c_0.dt, type='reverse', value=c_0.mark))
    return signals


def find_lowest(candles: List[Candle], dt):
    i = 0
    s = len(candles)
    lowest = 0
    while i < s:
        if candles[i].dt == dt:
            lowest = candles[i].low
            j = i - 1
            k = i + 1
            while j > 0:
                if candles[j].mark > 0:
                    break
                if candles[j].low < lowest:
                    lowest = candles[j].low
                j = j - 1
            while k < s:
                if candles[k].mark > 0:
                    break
                if candles[k].low < lowest:
                    lowest = candles[k].low
                k = k + 1
            break
        else:
            i = i + 1
    return lowest


def find_highest(candles: List[Candle], dt):
    i = 0
    s = len(candles)
    highest = 0
    while i < s:
        if candles[i].dt == dt:
            highest = candles[i].high
            j = i - 1
            k = i + 1
            while j > 0:
                if candles[j].mark < 0:
                    break
                if candles[j].high > highest:
                    highest = candles[j].high
                j = j - 1
            while k < s:
                if candles[k].mark < 0:
                    break
                if candles[k].high > highest:
                    highest = candles[k].high
                k = k + 1
            break
        else:
            i = i + 1
    return highest


if __name__ == '__main__':
    pass
    # re = Reverse()
    # search_all()

from entities.candle import Candle
from entities.signal import Signal
from typing import List
from storage.fetch import find_candles


def search_signal(code, klt):
    all_candles = find_candles(code, klt)
    mark_candles = []
    for cd in all_candles:
        if abs(cd.macd_mark) == 3:
            mark_candles.append(cd)
    size = len(mark_candles)
    signals = []
    for i in range(2, size):
        c_2 = mark_candles[i - 2]
        c_1 = mark_candles[i - 1]
        c_0 = mark_candles[i]
        if c_2.macd_mark == -3 and c_1.macd_mark == 3 and c_0.macd_mark == -3 and c_2.diff() < 0 and c_1.diff() < 0 and c_0.diff() < 0:
            low2 = find_lowest(all_candles, c_2.id)
            low0 = find_lowest(all_candles, c_0.id)
            if c_2.diff() < c_0.diff() and low2 > low0:
                signals.append(Signal(code=code, dt=c_0.dt, klt=klt, type=c_0.macd_mark))
        if c_2.macd_mark == 3 and c_1.macd_mark == -3 and c_0.macd_mark == 3 and c_2.diff() > 0 and c_1.diff() > 0 and c_0.diff() > 0:
            high2 = find_highest(all_candles, c_2.id)
            high0 = find_highest(all_candles, c_0.id)
            if c_2.diff() > c_0.diff() and high2 < high0:
                signals.append(Signal(code=code, dt=c_0.dt, klt=klt, type=c_0.macd_mark))
    print(signals)


def find_lowest(candles: List[Candle], id):
    i = 0
    s = len(candles)
    lowest = 0
    while i < s:
        if candles[i].id == id:
            lowest = candles[i].low
            j = i - 1
            k = i + 1
            while j > 0:
                if candles[j].macd_mark > 0:
                    break
                if candles[j].low < lowest:
                    lowest = candles[j].low
                j = j - 1
            while k < s:
                if candles[k].macd_mark > 0:
                    break
                if candles[k].low < lowest:
                    lowest = candles[k].low
                k = k + 1
            break
        else:
            i = i + 1
    return lowest


def find_highest(candles: List[Candle], id):
    i = 0
    s = len(candles)
    highest = 0
    while i < s:
        if candles[i].id == id:
            highest = candles[i].high
            j = i - 1
            k = i + 1
            while j > 0:
                if candles[j].macd_mark < 0:
                    break
                if candles[j].high > highest:
                    highest = candles[j].high
                j = j - 1
            while k < s:
                if candles[k].macd_mark < 0:
                    break
                if candles[k].high > highest:
                    highest = candles[k].high
                k = k + 1
            break
        else:
            i = i + 1
    return highest


if __name__ == '__main__':
    search_signal('300223', 101)

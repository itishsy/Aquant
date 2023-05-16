import datetime
from entities.candle import Candle
from entities.signal import Signal
from typing import List


def one_buy(candles: List[Candle]) -> Signal:
    signals = reverse(candles)
    if len(signals) > 0:
        signal = signals[-1]
        flag = False
        for c in candles:
            if c.dt == signal.dt:
                flag = True
            if flag:


    return None


def reverse(candles: List[Candle]) -> List[Signal]:
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
            down_stage1 = get_stage(candles, c_2.dt)
            down_stage2 = get_stage(candles, c_0.dt)
            if get_trend(down_stage1) == -1 and get_trend(down_stage2) == -1:
                low1 = get_lowest(down_stage1)
                low2 = get_lowest(down_stage2)
                if c_2.diff() < c_0.diff() and low1 > low2:
                    signals.append(Signal(dt=c_0.dt, type='reverse', value=c_0.mark))
        if c_2.mark == 3 and c_1.mark == -3 and c_0.mark == 3 and c_2.diff() > 0 and c_1.diff() > 0 and c_0.diff() > 0:
            up_stage1 = get_stage(candles, c_2.dt)
            up_stage2 = get_stage(candles, c_0.dt)
            if get_trend(up_stage1) == 1 and get_trend(up_stage2) == 1:
                high2 = get_highest(up_stage1)
                high0 = get_highest(up_stage2)
                if c_2.diff() > c_0.diff() and high2 < high0:
                    signals.append(Signal(dt=c_0.dt, type='reverse', value=c_0.mark))
    return signals


def get_lowest(candles: List[Candle]):
    lowest = candles[0]
    i = 1
    while i < len(candles):
        if candles[i].low < lowest.low:
            lowest = candles[i]
        i = i + 1
    return lowest


def get_highest(candles: List[Candle]):
    highest = candles[0]
    i = 1
    while i < len(candles):
        if candles[i].high > highest.high:
            highest = candles[i]
        i = i + 1
    return highest


def get_candle(candles: List[Candle], dt):
    i = 0
    while i < len(candles):
        if candles[i].dt == dt:
            return candles[i]
        i = i + 1
    return None



def get_stage(candles: List[Candle], dt) -> List[Candle]:
    """

    :param candles:
    :param dt:
    :return:
    """
    i = 0
    s = len(candles)
    stage = []
    while i < s:
        if candles[i].dt == dt:
            stage.append(candles[i])
            j = i - 1
            k = i + 1
            while j > 0:
                if (candles[j].mark > 0) == (candles[i].mark > 0):
                    stage.insert(0, candles[j])
                else:
                    break
                j = j - 1
            while k < s:
                if (candles[k].mark > 0) == (candles[i].mark > 0):
                    stage.append(candles[k])
                else:
                    break
                k = k + 1
            break
        i = i + 1
    return stage


def get_trend(candles: List[Candle]):
    """
    无趋势不背离
    :param candles:
    :return:
    """
    if len(candles) < 3:
        return 0
    i = 2
    while i < len(candles):
        if candles[i - 2].bar() > candles[i - 1].bar() > candles[i].bar():
            return -1
        if candles[i - 2].bar() < candles[i - 1].bar() < candles[i].bar():
            return 1
        i = i + 1
    return 0

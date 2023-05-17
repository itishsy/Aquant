from entities.candle import Candle
from entities.signal import Signal
from typing import List


def cal_klt(klt, add):
    if klt == 101:
        if add == -1:
            return 60
        elif add == -2:
            return 30
        elif add == -3:
            return 15
        elif add == 1:
            return 102
        else:
            return 0
    elif klt == 60:
        if add == 1:
            return 101
        elif add == -1:
            return 30
        elif add == -2:
            return 15
        else:
            return 0
    elif klt == 30:
        if add == 1:
            return 60
        elif add == 2:
            return 101
        elif add == -1:
            return 15
        else:
            return 0
    else:
        return 0


def deviates(candles: List[Candle], is_top=False) -> List[Signal]:
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
        if is_top:
            if c_2.mark == 3 and c_1.mark == -3 and c_0.mark == 3 and c_2.diff() > 0 and c_1.diff() > 0 and c_0.diff() > 0:
                up_stage1 = get_stage(candles, c_2.dt)
                up_stage2 = get_stage(candles, c_0.dt)
                if get_trend(up_stage1) == 1 and get_trend(up_stage2) == 1:
                    high2 = get_highest(up_stage1).high
                    high0 = get_highest(up_stage2).high
                    if c_2.diff() > c_0.diff() and high2 < high0:
                        signals.append(Signal(dt=c_0.dt, klt=c_0.klt, type='top_deviated', value=c_0.mark))
        else:
            if c_2.mark == -3 and c_1.mark == 3 and c_0.mark == -3 and c_2.diff() < 0 and c_1.diff() < 0 and c_0.diff() < 0:
                down_stage1 = get_stage(candles, c_2.dt)
                down_stage2 = get_stage(candles, c_0.dt)
                if get_trend(down_stage1) == -1 and get_trend(down_stage2) == -1:
                    low1 = get_lowest(down_stage1).low
                    low2 = get_lowest(down_stage2).low
                    if c_2.diff() < c_0.diff() and low1 > low2:
                        signals.append(Signal(dt=c_0.dt, klt=c_0.klt, type='bottom_deviated', value=c_0.mark))
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
    获取dt所处的bar一段，即起于下叉（上叉）终于上叉（下叉）的一段走势。
    准确的是用最高（低）那一根作为起点，不影响判断这一段走势是否有背驰。
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

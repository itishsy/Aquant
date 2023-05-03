from entities.candle import Candle
from entities.signal import Signal
from typing import List
from storage.fetch import find_candles, find_active_symbols
from enums.entity import Entity
from storage.db import db


def search_signal(code, klt, limit=200):
    session = db.get_session(Entity.Single)
    all_candles = find_candles(code, klt, limit=limit)
    print('========all_candles',all_candles)
    signals = do_reverse_search(all_candles)
    if len(signals) > 0:
        for sgn in signals:
            sgn.code = code
            sgn.klt = klt
        session.add_all(signals)
        session.commit()


def signal_all():
    sbs = find_active_symbols()
    for sb in sbs:
        search_signal(sb.code, 102)
        search_signal(sb.code, 101)
        search_signal(sb.code, 60)


def do_reverse_search(candles: List[Candle]) -> List[Signal]:
    mark_candles = []
    for cd in candles:
        if abs(cd.macd_mark) == 3:
            mark_candles.append(cd)
    size = len(mark_candles)
    signals = []
    for i in range(2, size):
        c_2 = mark_candles[i - 2]
        c_1 = mark_candles[i - 1]
        c_0 = mark_candles[i]
        if c_2.macd_mark == -3 and c_1.macd_mark == 3 and c_0.macd_mark == -3 and c_2.diff() < 0 and c_1.diff() < 0 and c_0.diff() < 0:
            low2 = find_lowest(candles, c_2.id)
            low0 = find_lowest(candles, c_0.id)
            if c_2.diff() < c_0.diff() and low2 > low0:
                signals.append(Signal(code='', klt=101, dt=c_0.dt, type='reverse', value=c_0.macd_mark))
        if c_2.macd_mark == 3 and c_1.macd_mark == -3 and c_0.macd_mark == 3 and c_2.diff() > 0 and c_1.diff() > 0 and c_0.diff() > 0:
            high2 = find_highest(candles, c_2.id)
            high0 = find_highest(candles, c_0.id)
            if c_2.diff() > c_0.diff() and high2 < high0:
                signals.append(Signal(code='', klt=101, dt=c_0.dt, type='reverse', value=c_0.macd_mark))
    return signals


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

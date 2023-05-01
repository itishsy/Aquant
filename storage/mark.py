from storage.db import db
from sqlalchemy import select, desc
from entities.candle import Candle
from typing import List


def mark(code, klt):
    session = db.get_session(code)
    unmark_candles = session.execute(
        select(Candle).where(Candle.klt == klt, Candle.macd_mark == None)
    ).scalars().fetchall()
    mark_candles = do_macd_mark(unmark_candles)
    mappings = []
    for cand in mark_candles:
        dic = {'id': cand.id, 'macd_mark': cand.macd_mark}
        mappings.append(dic)
    session.bulk_update_mappings(Candle, mappings)
    session.flush()
    session.commit()


def do_macd_mark(candles: List[Candle]) -> List[Candle]:
    size = len(candles)

    for c in candles:
        c.macd_mark = 1 if c.bar() > 0 else -1

    for i in range(2, size):
        c_2 = candles[i - 2]
        c_1 = candles[i - 1]
        c_0 = candles[i]
        if c_2.macd_mark == c_1.macd_mark == c_0.macd_mark == -1:
            if c_2.diff() > c_1.diff() < c_0.diff():
                c_1.macd_mark = -3
        if c_2.macd_mark == c_1.macd_mark == c_0.macd_mark == 1:
            if c_2.diff() < c_1.diff() > c_0.diff():
                c_1.macd_mark = 3

    i = 2
    while i < size:
        if abs(candles[i].macd_mark) < 3:
            i = i + 1
            continue

        if candles[i].macd_mark == -3:
            min_diff = candles[i].diff()
            j = i + 1
            while j < size:
                if candles[j].macd_mark > 0:
                    break
                if candles[j].macd_mark == -3:
                    if min_diff > candles[j].diff():
                        candles[i].macd_mark = -2
                        min_diff = candles[j].diff()
                    else:
                        candles[j].macd_mark = -2
                j = j + 1
            i = j

        if candles[i].macd_mark == 3:
            max_diff = candles[i].diff()
            j = i + 1
            while j < size:
                if candles[j].macd_mark < 0:
                    break
                if candles[j].macd_mark == 3:
                    if max_diff < candles[j].diff():
                        candles[i].macd_mark = 2
                        max_diff = candles[j].diff()
                    else:
                        candles[j].macd_mark = 2
                j = j + 1
            i = j
    return candles


if __name__ == '__main__':
    mark('300223', 101)
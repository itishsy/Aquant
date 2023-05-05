from typing import List
from storage.db import db
from entities.candle import Candle
from sqlalchemy import select


def mark(candles: List[Candle]) -> List[Candle]:
    size = len(candles)

    for c in candles:
        c.mark = 1 if c.bar() > 0 else -1

    for i in range(2, size):
        c_2 = candles[i - 2]
        c_1 = candles[i - 1]
        c_0 = candles[i]
        if c_2.diff() < 0 and c_1.diff() < 0 and c_0.diff() < 0:
            if c_2.mark == c_0.mark == -1 and c_1.mark == 1:
                if c_2.diff() > c_1.diff() < c_0.diff():
                    c_1.mark = -3
            if c_2.mark == c_0.mark == 1 and c_1.mark == -1:
                if c_2.diff() < c_1.diff() > c_0.diff():
                    c_1.mark = 3

    i = 2
    while i < size:
        if abs(candles[i].mark) < 3:
            i = i + 1
            continue

        if candles[i].mark == -3:
            min_diff = candles[i].diff()
            j = i + 1
            while j < size:
                if candles[j].mark > 0:
                    break
                if candles[j].mark == -3:
                    if min_diff > candles[j].diff():
                        candles[i].mark = -2
                        min_diff = candles[j].diff()
                    else:
                        candles[j].mark = -2
                j = j + 1
            i = j

        if i < size and candles[i].mark == 3:
            max_diff = candles[i].diff()
            j = i + 1
            while j < size:
                if candles[j].mark < 0:
                    break
                if candles[j].mark == 3:
                    if max_diff < candles[j].diff():
                        candles[i].mark = 2
                        max_diff = candles[j].diff()
                    else:
                        candles[j].mark = 2
                j = j + 1
            i = j
    return candles


def remark(code, klt):
    session = db.get_session(code)
    unmark_candles = session.execute(
        select(Candle).where(Candle.klt == klt, Candle.mark == None)
    ).scalars().fetchall()
    mark_candles = mark(unmark_candles)
    mappings = []
    for cad in mark_candles:
        dic = {'id': cad.id, 'mark': cad.mark}
        mappings.append(dic)
    session.bulk_update_mappings(Candle, mappings)
    session.flush()
    session.commit()

from typing import List
from storage.db import db, find_active_symbols
from entities.candle import Candle
from sqlalchemy import select,and_


def mark(candles: List[Candle]) -> List[Candle]:
    size = len(candles)
    if size == 0:
        return candles

    for c in candles:
        c.mark = 1 if c.bar() > 0 else -1

    for i in range(2, size):
        c_2 = candles[i - 2]
        c_1 = candles[i - 1]
        c_0 = candles[i]
        if c_2.mark == c_0.mark == c_1.mark == -1:
            if c_2.diff() > c_1.diff() < c_0.diff():
                c_1.mark = -3
        if c_2.mark == c_0.mark == c_1.mark == 1:
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
                        i = j
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
                        i = j
                    else:
                        candles[j].mark = 2
                j = j + 1
            i = j
    return candles


def remark(code, freq, beg=None):
    session = db.get_session(code)
    clauses = and_(Candle.freq == freq)
    if beg is not None:
        clauses = clauses.__and__(Candle.dt > beg)
    candles = session.execute(select(Candle).where(clauses)).scalars().fetchall()
    mark_candles = mark(candles)
    mappings = []
    for cad in mark_candles:
        dic = {'id': cad.id, 'mark': cad.mark}
        mappings.append(dic)
    session.bulk_update_mappings(Candle, mappings)
    session.flush()
    session.commit()


if __name__ == '__main__':
    codes = ['002292','002997']
    # remark('300031', 101)
    symbols = find_active_symbols()
    for sbl in symbols:
        if len(codes) > 0 and sbl.code not in codes:
            continue
        try:
            remark(sbl.code, 102)
            remark(sbl.code, 101)
            remark(sbl.code, 60)
            remark(sbl.code, 30)
            remark(sbl.code, 15)
        except:
            print('{} mark error'.format(sbl.code))
        finally:
            print('{} mark finish'.format(sbl.code))


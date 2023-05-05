from enums.entity import Entity
from signals.strategy import Strategy
from storage.db import db , find_candles
from entities.candle import Candle
from entities.signal import Signal



def search_signal(code, klt=101):
    session = db.get_session(Entity.Signal)
    candles = find_candles(code, klt)
    size = len(candles)
    signals = []
    cross_index = 0
    for i in range(2, size):
        c_0 = candles[i]
        if not is_above(c_0):
            cross_index = 0
            continue
        c_1 = candles[i - 1]
        if is_gold_cross(c_1, c_0):
            if cross_index > 1:
                signals.append(Signal(code=code, dt=c_0.dt, klt=klt, type=Strategy.gold_cross, value=c_0.mark))
            cross_index = cross_index + 1

    if len(signals) > 0:
        session.add_all(signals)
        session.commit()


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



if __name__ == '__main__':
    search_signal('300223', 101)

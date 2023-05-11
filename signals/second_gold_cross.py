import datetime

from signals.strategy import register_strategy, Strategy
from entities.candle import Candle
from entities.signal import Signal
from typing import List
from storage.fetcher import fetch_data, fetch_and_save
from signals.reverse import search_reverse


@register_strategy
class SecondGoldCross(Strategy):

    def search_signal(self, candles: List[Candle]) -> List[Signal]:
        # 0轴上方的macd调整出现的买点
        # 最后一个mark段为-3_3_-3，其中3_-3均在零轴上方，
        # 3_-3段出现次某级别的reverse买点
        # 回落段3_-3幅度不能超过上涨段(-3_3)幅度的0.618
        mark_candles = []
        for cd in candles:
            if abs(cd.mark) == 3:
                mark_candles.append(cd)
        m_size = len(mark_candles)
        i = 2
        signals = []
        while i < m_size:
            c_3 = mark_candles[i - 2]
            c_2 = mark_candles[i - 1]
            c_1 = mark_candles[i]
            if c_3.mark == -3 and c_2.mark == 3 and c_1.mark == -3:
                if is_above(c_2) and is_above(c_1):
                    if (c_2.high - c_1.low) / (c_2.high - c_3.low) > 0.5:
                        for klt in [15, 30, 60]:
                            c_candles = fetch_data(self.code, klt, c_3.dt.replace('-', ''))
                            sis = search_reverse(c_candles)
                            for si in sis:
                                if c_1.dt > si.dt > c_2.dt:
                                    si.klt = klt
                                    si.type = 'second_gold_cross'
                                    signals.append(si)
            i = i + 1
        return signals


def is_above(candle: Candle):
    # 是否在0轴上方
    if candle.diff() > 0 and candle.dea9 > 0:
        return True
    else:
        return False


if __name__ == '__main__':
    sub_candles = fetch_and_save('300133', 15)


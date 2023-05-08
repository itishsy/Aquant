from signals.strategy import register_strategy, Strategy
from entities.candle import Candle
from entities.signal import Signal
from typing import List
from storage.fetcher import fetch_data
from signals.reverse import Reverse


@register_strategy
class GoldCross(Strategy):
    code = None

    def search_signal(self, candles: List[Candle]) -> List[Signal]:
        # 0轴上方的macd调整出现的买点
        # 最后一个mark段为-3_3_-3，其中3_-3均在零轴上方，
        # 3_-3段出现次某级别的reverse买点
        # 回落段3_-3幅度不能超过上涨段(-3_3)幅度的0.618，或0.5
        mark_candles = []
        for cd in candles:
            if abs(cd.mark) == 3:
                mark_candles.append(cd)
        m_size = len(mark_candles)
        c_3 = mark_candles[m_size - 3]
        c_2 = mark_candles[m_size - 2]
        c_1 = mark_candles[m_size - 1]
        signals = []
        if c_3.mark == -3 and c_2.mark == 3 and c_1.mark == -3:
            if is_above(c_2) and is_above(c_1):
                if (c_2.high - c_1.low) / (c_2.high - c_3.low) > 0.618:
                    sub_candles = fetch_data(self.code, 30, c_3.dt)
                    rev = Reverse()
                    signals = rev.search_signal(sub_candles)
        return signals


def is_above(candle: Candle):
    # 是否在0轴上方
    if candle.diff() > 0 and candle.dea9 > 0:
        return True
    else:
        return False


if __name__ == '__main__':
    gold = GoldCross()
    gold.search_all()

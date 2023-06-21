from strategies.strategy import register_strategy, Strategy
from storage.dba import freqs, find_stage_candles, find_candles
import signals.utils as sig
from models.signal import Signal
from datetime import datetime, timedelta
from decimal import Decimal
from signals.divergence import diver_bottom
from storage.candle import Candle
from typing import List


@register_strategy
class DRC(Strategy):
    def search(self, candles: List[Candle]):
        """ 下跌趋势反转策略
        满足以下条件：
        1. 大级别最近的快慢线交叉发生在0轴上方,50%以上diff在0轴上方
        2. 本级别发生底背离
        3. 反弹后回落向下确认，快线不破慢线，发生孙子级别的一买。
        :param candles:
        """

        sis = diver_bottom(candles)
        if len(sis) == 0:
            return

        # 最后一个背离signal
        si = sis[-1]

        # 父級別的一段起點在0轴上方
        psc = find_stage_candles(self.code, self.parent_freq(), sig.get_candle(candles, si.dt))
        if len(psc) < 2 or psc[0].dea9 < 0:
            return

        # 获取底部形态的5段
        d, a, b, r, c = sig.get_dabrc(candles, si.dt)
        if a is None or r is None or c is None:
            return

        # c段不可跌破b段最低点
        c3 = candles[-1] if c is None else sig.get_lowest(c)
        b3 = sig.get_lowest(b)
        if c3 is None or b3 is None or c3.low < b3.low:
            return

        # 反弹空间力度不够
        gold_line = sig.get_lowest(a).low + (sig.get_highest(a).high - sig.get_lowest(a).low) * Decimal(0.5)
        if gold_line > Decimal(sig.get_highest(r).high):
            return

        # c段发生次级别背离
        sdt = si.dt
        for fre in self.child_freq():
            ccs = find_candles(self.code, fre, begin=sdt, end=c[-1].dt)
            dbs = diver_bottom(ccs)
            if len(dbs) == 0:
                continue
            sign = dbs[-1]
            sign.source = self.__class__.__name__
            sign.value = fre
            sign.code = self.code
            self.signals.append(sign)

    def deal(self, code):
        pass

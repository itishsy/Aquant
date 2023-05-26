from strategies.strategy import register_strategy, Strategy
from storage.db import find_stage_candles, find_candles, freqs
import signals.utils as sig
from storage.fetcher import fetch_data
from storage.marker import mark
from entities.signal import Signal
from datetime import datetime
from decimal import Decimal


@register_strategy
class DRC(Strategy):
    def search(self, code):
        """ 下跌趋势反转策略
        满足以下条件：
        1. 大级别最近的快慢线交叉发生在0轴上方,50%以上diff在0轴上方
        2. 本级别发生底背离
        3. 反弹后回落向下确认，快线不破慢线，发生孙子级别的一买。
        :param code:
        """
        candles = find_candles(code, self.freq, begin=self.begin, limit=self.limit)
        if len(candles) < self.limit:
            return

        sis = sig.divergence(candles)
        if len(sis) == 0:
            return

        # 最后一个背离signal
        si = sis[-1]

        # 背离点所在父級別一段，大部分是在0轴上方
        psc = find_stage_candles(code, self.parent_freq(), sig.get_candle(candles, si.dt))
        pos = int(len(psc) * 0.618)
        if len(psc) < 2 or psc[:pos][-1].dea9 < 0:
            return

        # 获取底部形态的5段
        d, a, b, r, c = sig.get_dabrc(candles, si.dt)
        if a is None or r is None or c is None:
            return

        # 反弹段要有向上叉
        if sig.has_cross(r) < 1:
            return

        # c段不可跌破b段最低点
        c3 = candles[-1] if c is None else sig.get_lowest(c)
        b3 = sig.get_lowest(b)
        if c3 is None or b3 is None or c3.low < b3.low:
            return

        # c段不可连续击穿慢线
        if sig.has_cross(c) == -1:
            i = 1
            while i < len(c):
                if c[i - 1].bar() < 0 and c[i].bar() < 0:
                    return
                i = i + 1

        # 反弹空间力度不够
        gold_line = sig.get_lowest(a).low + (sig.get_highest(a).high - sig.get_lowest(a).low) * Decimal(0.5)
        if gold_line > Decimal(sig.get_highest(r).high):
            return

        # 反弹时间力度不够
        if len(b) > len(r):
            pass

        si = Signal(c3.dt, self.freq, type=self.__class__.__name__, value=c3.mark)
        si.code = code
        si.value = self.freq
        si.created = datetime.now()
        self.signals.append(si)

        if sig.has_trend(c):
            if self.freq > 100:
                sdt = datetime.strptime(c[0].dt, '%Y-%m-%d')
            else:
                sdt = datetime.strptime(c[0].dt, '%Y-%m-%d %H:%M')
            # c段有一段小走势,查小级别的背离信号
            for ck in self.grandchild_freq():
                if ck not in freqs:
                    ccs = fetch_data(code, ck, begin=sdt.strftime('%Y%m%d'))
                    ccs = mark(ccs)
                else:
                    ccs = find_candles(code, ck, begin=c[0].dt, end=c[-1].dt)
                self.append_signals(code, ccs)

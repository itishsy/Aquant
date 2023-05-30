from strategies.strategy import register_strategy, Strategy
from storage.db import freqs
import signals.utils as sig
from models.signal import Signal
from models.candle import find_stage_candles,find_candles
from datetime import datetime
from decimal import Decimal
from signals.divergence import diver_bottom


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

        sis = diver_bottom(candles)
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

        # 反弹空间力度不够
        gold_line = sig.get_lowest(a).low + (sig.get_highest(a).high - sig.get_lowest(a).low) * Decimal(0.5)
        if gold_line > Decimal(sig.get_highest(r).high):
            return

        # 反弹时间力度不够
        if len(b) > len(r):
            pass

        # c段不可连续击穿慢线
        if sig.has_cross(c) == -1:
            if sig.get_highest(c).diff()>0:
                # 高点在0轴之上,找子级别的背离
                for fre in self.child_freq():
                    if fre in freqs:
                        ccs = find_candles(code, fre, begin=c[0].dt, end=c[-1].dt)
                        dbs = diver_bottom(ccs)
                        ss = []
                        for cs in dbs:
                            cs.type = self.__class__.__name__,
                            cs.value = cs.freq
                            cs.freq = self.freq
                            cs.code = code
                            cs.created = datetime.now()
                            ss.append(cs)
                        self.upset_signals(ss)
                return
            else:
                # 高点在0轴之下不可连续击穿慢线
                i = 1
                while i < len(c):
                    if c[i - 1].bar() < 0 and c[i].bar() < 0:
                        return
                    i = i + 1

        # 倒三角bar
        i = 2
        while i < len(c):
            if c[i].bar() > c[i - 1].bar() < c[i - 2].bar() < c[i].bar():
                si = Signal(c[i].dt, self.freq, type=self.__class__.__name__, value=c3.mark)
                si.code = code
                si.value = self.freq
                si.created = datetime.now()
                self.signals.append(si)

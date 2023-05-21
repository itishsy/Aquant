from strategies.strategy import register_strategy, Strategy
from storage.db import find_stage_candles, find_candles, kls
import signals.signals as sig
from storage.fetcher import fetch_data
from entities.signal import Signal
from datetime import datetime


@register_strategy
class DRC(Strategy):
    def search(self, code):
        """ 下跌趋势反转策略，找出所有处在C段确认的
        满足以下条件：
        1. 大级别最近的快慢线交叉发生在0轴上方,50%以上diff在0轴上方
        2. 本级别发生底背离
        3. 反弹后回落向下确认，快线不破慢线，发生孙子级别的一买。
        :param code:
        """
        candles = find_candles(code, self.klt, begin=self.begin, limit=self.limit)
        if len(candles) < self.limit:
            return

        sis = sig.divergence(candles)
        if len(sis) == 0:
            return

        # 只获取最后一个
        si = sis[-1]
        sdt = si.dt

        # 判断父級別的一段是否符合
        psc = find_stage_candles(code, self.parent_klt(), sig.get_candle(candles, sdt))
        if len(psc) < 2 or psc[:len(psc) // 2][-1].dea9 < 0:
            return

        m3 = []
        for cd in candles:
            if cd.mark == 3 or cd.mark == -3:
                m3.append(cd)

        b_stage = sig.get_stage(candles, si.dt)
        b3 = sig.get_lowest(b_stage)

        a3 = None  # A段
        r3 = None  # R段
        c3 = None  # C段
        l = len(m3) - 1
        while l > 1:
            if m3[l].dt == sdt:
                if l + 1 < len(m3):
                    r3 = m3[l + 1]
                if l + 2 < len(m3):
                    c3 = m3[l + 2]
                a3 = m3[l - 1]
                break
            l = l - 1

        # 有力度的反弹
        if a3 is None or r3 is None or a3.high > r3.high:
            return
        if c3 is None:
            c3 = candles[-1]

        # 确认段跌破背驰段，C段无效
        if c3.low < b3.low or c3.bar() < 0:
            return

        # C段要有一段小趋势
        sts = find_candles(code, self.klt, begin=r3.dt)

        # C段不可连续击穿慢线。
        flag = True
        i = 0
        while i < len(sts):
            if sts[i - 1].bar() < 0 and sts[i].bar() < 0:
                return
            # C段回调有三根递减的bar
            if sts[i - 2].bar() > sts[i - 1].bar() > sts[i].bar():
                flag = False
            i = i + 1

        if flag:
            # c3是信号
            si = Signal(c3.dt, self.klt, type=self.__class__.__name__, value=c3.mark)
            si.code = code
            si.created = datetime.now()
            self.signals.append(si)
        else:
            # C段孙子级别的背离
            for ck in self.child_child_klt():
                if ck not in kls:
                    ccs = fetch_data(code, ck, begin=sdt)
                else:
                    ccs = find_candles(code, ck, begin=sdt, end=c3.dt)
                self.append_signals(code, ccs)

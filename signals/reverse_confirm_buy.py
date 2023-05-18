from datetime import datetime, timedelta
from entities.candle import Candle
from entities.signal import Signal
from typing import List
from signals.strategy import register_strategy, Strategy, reverse_signals, factory, get_candle
from storage.db import find_candles, update_all_symbols, find_signals, find_stage_candles
from storage.fetcher import fetch_all
import signals.signals as sig


@register_strategy
class RCB(Strategy):
    def search_signal(self, candles: List[Candle]) -> List[Signal]:
        """ 反转确认买点
        满足以下条件：
        1. 大级别最近的快慢线交叉发生在0轴上方,50%以上diff在0轴上方
        2. 本级别发生底背离
        3. 反弹后回落向下确认，快线不破慢线，发生次某级别的一买。
        :param candles:
        :return:
        """
        signals = []
        sis = sig.deviates(candles)
        ss = []
        print('[{}] {} found deviates: {}'.format(datetime.now(), self.code, len(sis)))
        # cond1: 父级别的一段在大部分在0轴上方
        for si in sis:
            if si.value == -3:
                if self.klt > 100:
                    scs = find_stage_candles(self.code, 102, get_candle(candles, si.dt))
                else:
                    scs = find_stage_candles(self.code, 101, get_candle(candles, si.dt))

                a_flag = True
                ha = int((len(scs) / 2))
                sc2 = scs[:ha]
                for sc in sc2:
                    if sc.diff() < 0 or sc.dea9 < 0:
                        a_flag = False
                        break
                if a_flag:
                    ss.append(si)
        if len(ss) == 0:
            return signals

        # 获取底背离信号－3后第一个mart=3右边的dt
        flag = False
        flag_3 = False
        dt = None
        lowest = None
        for c in candles:
            if flag_3:
                dt = c.dt
            if c.dt == ss[-1].dt:
                flag = True
                lowest = c.low
            if flag and c.mark == 3:
                flag_3 = True
                flag = False

        if dt is None:
            return signals

        # 判断confirm段(3,-3)是否满足
        i = 2
        sts = sig.get_stage(candles, dt)
        while i < len(sts):
            if sts[i - 1].bar() < 0 and sts[i].bar() < 0:
                break
            elif (sts[i - 2].bar() > sts[i - 1].bar() < sts[i].bar()) and (
                    sts[i - 2].low > sts[i - 1].low < sts[i].low) and lowest < sts[i - 1].low:
                signals.append(
                    Signal(dt=sts[i].dt, klt=sts[i - 1].klt, type=self.__class__.__name__, value=sts[i].mark))
            i = i + 1
        return signals


if __name__ == '__main__':
    cs = '301220,600795'
    begin = datetime.now()
    update_all_symbols(status=0, beyond=cs)
    fetch_all()
    st = factory['BottomConfirm']()
    st.search_all()
    print(find_signals(begin=begin))

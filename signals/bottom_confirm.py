from datetime import datetime, timedelta
from entities.candle import Candle
from entities.signal import Signal
from typing import List
from signals.strategy import register_strategy, Strategy, reverse_signals, factory, get_candle
from storage.db import find_candles, update_all_symbols, find_signals
from storage.fetcher import fetch_all


@register_strategy
class BottomConfirm(Strategy):
    def search_signal(self, candles: List[Candle]) -> List[Signal]:
        """ 底部确认信号
        满足以下条件：
        1. 大级别最近的快慢线交叉发生在0轴上方。
        2. 本级别发生底背离
        3. 反弹后回落向下确认，快线不破慢线，发生次某级别的一买。
        :param candles:
        :return:
        """
        signals = []
        sis = reverse_signals(candles)
        ss = []
        for si in sis:
            if si.value == -3:
                if self.klt in [60, 101]:
                    a_flag = True
                    if self.klt == 101:
                        beg = datetime.strptime(si.dt, '%Y-%m-%d') - timedelta(30 * 5)
                        kl = 102
                    else:
                        beg = datetime.strptime(si.dt, '%Y-%m-%d %H:%M') - timedelta(30 * 5)
                        kl = 101
                    wcs = find_candles(self.code, kl, begin=beg.strftime('%Y-%m-%d'), end=si.dt)
                    wi = len(wcs) - 1
                    while wi > 1:
                        if wcs[wi].mark == 3 and (wcs[wi].diff() < 0 or wcs[wi].bar() < 0):
                            a_flag = False
                            break
                        if wcs[wi - 1].bar() > 0 > wcs[wi].bar() and (wcs[wi - 1].diff() < 0 or wcs[wi - 1].bar() < 0):
                            a_flag = False
                            break
                        wi = wi - 1
                    if a_flag:
                        ss.append(si)
        if len(ss) == 0:
            return signals

        i = 0
        s = 0
        s_flag = False
        c_flag = False
        sdt = ss[0].dt
        while i < len(candles):
            if s < len(ss) and candles[i].dt == ss[s].dt:
                s_flag = True
                sdt = ss[s].dt
                s = s + 1
            if s_flag and i > 1 and candles[i - 1].bar() < 0 < candles[i].bar():
                c_flag = True
                s_flag = False
            if c_flag:
                if candles[i].bar() < 0 and candles[i - 1].bar() < 0:
                    c_flag = False
                else:
                    c_2 = candles[i - 2]
                    c_1 = candles[i - 1]
                    c_0 = candles[i]
                    if (c_2.bar() > c_1.bar() < c_0.bar()) and (c_2.low > c_1.low < c_0.low):
                        if get_candle(candles, sdt).low < c_1.low:
                            signals.append(Signal(dt=c_0.dt, type=self.__class__.__name__, value=c_0.mark))
                        c_flag = False
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

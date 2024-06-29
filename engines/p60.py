from engines.engine import strategy_engine, Engine
from candles.storage import find_candles
from signals.divergence import diver_bottom, diver_top
from models.signal import Signal
from models.choice import Choice
from strategies.pab import Pab
import signals.utils as utl


@strategy_engine
class P60(Engine):

    def find_choice_signal(self, code):
        pab = Pab()
        pab.code = code
        pab.freq = 60
        sig = pab.search()
        if sig:
            sig.type = 'diver-bottom'
        return sig

    def find_buy_signal(self, cho):
        if cho.cid is None:
            return

        c_sig = Signal.get(Signal.id == cho.cid)
        if c_sig:
            return self.common_buy_point(c_sig, 15)

    def find_out_signal(self, cho: Choice):
        if cho.cid is None:
            return
        c_sig = Signal.get(Signal.id == cho.cid)
        cds = find_candles(cho.code, begin=c_sig.dt)

        # 超时不出b_signal
        if len(cds) > 20:
            return Signal(code=cho.code, name=cho.name, freq=101, dt=cds[-1].dt, type='timeout')

        lowest = utl.get_lowest(cds)
        # 快慢线均回落到0轴之下
        if lowest.dea9 < 0 and lowest.diff() < 0:
            return Signal(code=cho.code, name=cho.name, freq=101, dt=lowest.dt, type='lowest')

        # 跌破c_sig价
        if lowest and lowest.low < c_sig.price:
            return Signal(code=cho.code, name=cho.name, freq=101, dt=lowest.dt, type='damage')

    def find_sell_signal(self, cho):
        if cho.bid is None:
            return
        b_sig = Signal.get(Signal.id == cho.bid)

        # 15min顶背离
        cds1 = self.fetch_candles(code=cho.code, freq=15)
        dts = diver_top(cds1)
        if len(dts) > 0:
            sig = dts[-1]
            if sig.dt > b_sig.dt:
                sig.type = 'diver-top'
                return sig

        # 日k长上影线
        cds2 = find_candles(code=cho.code, begin=cho.dt)
        highest = utl.get_highest(cds2)
        if utl.is_upper_shadow(highest):
            return Signal(code=cho.code, name=cho.name, freq=highest.freq, dt=highest.dt, type='up-shadow')

        # 60min下叉
        cds60 = find_candles(code=cho.code, freq=60, begin=cho.dt)
        cross30 = utl.get_cross(cds60)
        if cross30[-1].mark == 1:
            return Signal(code=cho.code, name=cho.name, freq=60, dt=cross30[-1].dt, type='cross-down')


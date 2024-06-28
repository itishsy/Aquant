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

        sig60 = Signal.get(Signal.id == cho.cid)
        if sig60:
            cds = self.fetch_candles(code=cho.code, freq=10, begin=sig60.dt)
            db10 = diver_bottom(cds)
            if len(db10) > 0:
                sig10 = db10[-1]
                if sig10.price > sig60.price:
                    sig10.type = 'diver_bottom'
                    return sig10

    def find_out_signal(self, cho: Choice):
        if cho.cid is None:
            return
        sig60 = Signal.get(Signal.id == cho.cid)
        cds = find_candles(cho.code, begin=sig60.dt)
        # 超时不出b_signal
        if len(cds) > 20:
            return Signal(code=cho.code, name=cho.name, freq=sig60.freq, dt=cds[-1].dt, type='timeout')
        lowest = utl.get_lowest(cds)
        # 快慢线均回落到0轴之下
        if lowest.dea9 < 0 and lowest.diff() < 0:
            return Signal(code=cho.code, name=cho.name, freq=sig60.freq, dt=lowest.dt, type='lowest')
        # c_signal跌破最低价
        if lowest and lowest.low < sig60.price:
            return Signal(code=cho.code, name=cho.name, freq=sig60.freq, dt=lowest.dt, type='damage')

    def find_sell_signal(self, cho):
        if cho.bid is None:
            return
        sig10 = Signal.get(Signal.id == cho.bid)

        cds10 = self.fetch_candles(code=cho.code, freq=10, begin=sig10.dt)
        dt10 = diver_top(cds10)
        if len(dt10) > 0:
            sig = dt10[-1]
            sig.type = 'diver-top'
            return sig

        cds = find_candles(code=cho.code, begin=cho.dt)
        highest = utl.get_highest(cds)
        if utl.is_upper_shadow(highest):
            return Signal(code=cho.code, name=cho.name, freq=highest.freq, dt=highest.dt, type='shadow')

        cds60 = find_candles(code=cho.code, freq=60, begin=cho.dt)
        cross30 = utl.get_cross(cds60)
        if cross30[-1].mark == 1:
            return Signal(code=cho.code, name=cho.name, freq=60, dt=cross30[-1].dt, type='cross-down')


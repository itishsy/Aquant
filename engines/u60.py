from engines.engine import strategy_engine, Engine
from candles.storage import find_candles
from signals.divergence import diver_bottom, diver_top
from models.signal import Signal
from models.choice import Choice
from strategies.uab import Uab
import signals.utils as utl


@strategy_engine
class U60(Engine):

    def find_choice_signal(self, code):
        uab = Uab()
        uab.code = code
        uab.ma = 60
        uab.mrate = 0.8
        uab.freq = 60
        sig = uab.search()
        if sig:
            sig.type = 'diver-bottom'
        return sig

    def find_buy_signal(self, cho):
        if cho.cid is None:
            return

        sig60 = Signal.get(Signal.id == cho.cid)
        if sig60:
            cds = self.fetch_candles(code=cho.code, freq=15, begin=sig60.dt)
            db15 = diver_bottom(cds)
            if len(db15) > 0:
                sig15 = db15[-1]
                if sig15.price > sig60.price:
                    sig15.type = 'diver-bottom'
                    return sig15

    def find_out_signal(self, cho: Choice):
        if cho.cid is None:
            return
        sig60 = Signal.get(Signal.id == cho.cid)
        cds = find_candles(cho.code, begin=sig60.dt)
        # 超时不出b_signal
        if len(cds) > 15:
            return Signal(code=cho.code, name=cho.name, freq=sig60.freq, dt=cds[-1].dt, type='timeout')
        # c_signal破坏
        lowest = utl.get_lowest(cds)
        if lowest and lowest.low < sig60.price:
            return Signal(code=cho.code, name=cho.name, freq=sig60.freq, dt=cds[-1].dt, type='damage')

    def find_sell_signal(self, cho):
        if cho.bid is None:
            return
        sig15 = Signal.get(Signal.id == cho.bid)

        cds15 = self.fetch_candles(code=cho.code, freq=15, begin=sig15.dt)
        dt15 = diver_top(cds15)
        if len(dt15) > 0:
            sig = dt15[-1]
            sig.type = 'diver-top'
            return sig

        cds60 = find_candles(code=cho.code, freq=60, begin=sig15.dt)
        highest = utl.get_highest(cds60)
        if utl.is_upper_shadow(highest):
            return Signal(code=cho.code, name=cho.name, freq=sig15.freq, dt=highest.dt, type='shadow')


from engines.engine import strategy_engine, Engine
from candles.storage import find_candles
from signals.divergence import diver_bottom, diver_top
from models.signal import Signal
from models.choice import Choice
from strategies.uab import Uab
import signals.utils as utl


@strategy_engine
class U30(Engine):

    def find_choice_signal(self, code):
        uab = Uab()
        uab.code = code
        uab.ma = 30
        uab.mrate = 0.7
        uab.freq = 30
        return uab.search()

    def find_buy_signal(self, cho):
        if cho.cid is None:
            return

        sig30 = Signal.get(Signal.id == cho.cid)
        if sig30:
            cds = self.fetch_candles(code=cho.code, freq=5, begin=sig30.dt)
            db5 = diver_bottom(cds)
            if len(db5) > 0:
                sig5 = db5[-1]
                if sig5.price > sig30.price:
                    return sig5

    def find_out_signal(self, cho: Choice):
        if cho.cid is None:
            return
        sig30 = Signal.get(Signal.id == cho.cid)
        cds = find_candles(cho.code, begin=sig30.dt)
        # 超时不出b_signal
        if len(cds) > 10:
            return Signal(code=cho.code, name=cho.name, dt=cds[-1].dt, strategy='Timeout')
        # c_signal破坏
        lowest = utl.get_lowest(cds)
        if lowest.low < sig30.price:
            return Signal(code=cho.code, name=cho.name, dt=cds[-1].dt, strategy='Damage')

    def find_sell_signal(self, cho):
        if cho.bid is None:
            return
        sig5 = Signal.get(Signal.id == cho.bid)

        cds5 = self.fetch_candles(code=cho.code, freq=5, begin=sig5.dt)
        dt5 = diver_top(cds5)
        if len(dt5) > 0:
            return dt5[-1]

        cds30 = find_candles(code=cho.code, freq=30, begin=sig5.dt)
        highest = utl.get_highest(cds30)
        if utl.is_upper_shadow(highest):
            return Signal(code=cho.code, name=cho.name, dt=highest.dt, strategy='shadow')


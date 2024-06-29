from engines.engine import strategy_engine, Engine
from candles.storage import find_candles
from signals.divergence import diver_bottom, diver_top
from models.signal import Signal
from models.choice import Choice
from strategies.uab import Uab
import signals.utils as utl


@strategy_engine
class U60(Engine, Uab):

    def find_choice_signal(self, code):
        sig = self.search(code=code, freq=60, mfreq=60, mrate=0.8)
        if sig:
            sig.type = 'diver-bottom'
        return sig

    def find_buy_signal(self, c_sig: Signal):
        sig = self.common_buy_point(c_sig, 15)
        if not sig:
            return self.buy_point(c_sig, 15)

    def find_out_signal(self, c_sig: Signal):
        sig = self.common_out(c_sig, timeout=20)
        if not sig:
            return self.out(c_sig)

    def find_sell_signal(self, c_sig: Signal, b_sig: Signal):
        sig = self.common_sell_point(c_sig, b_sig.freq)
        if not sig:
            sig = self.sell_point(c_sig, b_sig)
        return sig

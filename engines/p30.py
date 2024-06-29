from engines.engine import strategy_engine, Engine
from candles.storage import find_candles
from signals.divergence import diver_bottom, diver_top
from models.signal import Signal
from models.choice import Choice
from strategies.pab import Pab
import signals.utils as utl


@strategy_engine
class P30(Engine, Pab):
    def find_choice_signal(self, code):
        sig = self.search(code, 30)
        if sig:
            sig.type = 'diver-bottom'
            return sig

    def find_buy_signal(self, c_sig: Signal):
        sig = self.common_buy_point(c_sig, 5)
        if not sig:
            sig = self.buy_point(c_sig, 5)
        return sig

    def find_out_signal(self, c_sig: Signal):
        sig = self.common_out(c_sig, timeout=10)
        if not sig:
            sig = self.out(c_sig)
        return sig

    def find_sell_signal(self, c_sig: Signal, b_sig: Signal):
        return self.sell_point(c_sig, b_sig)

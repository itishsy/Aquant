from engines.engine import strategy_engine, Engine
from models.signal import Signal
from strategies.pab import Pab
from datetime import datetime, timedelta


@strategy_engine
class P60(Engine, Pab):
    def find_choice_signal(self, code):
        sig = self.search(code, 60)
        if sig:  # and sig.dt > (datetime.now() - timedelta(days=20)).strftime('%Y-%m-%d'):
            sig.type = 'diver-bottom'
            return sig

    def find_buy_signal(self, c_sig: Signal):
        sig = self.common_buy_point(c_sig, 15)
        if not sig:
            sig = self.buy_point(c_sig, 15)
        if not sig:
            sig = self.common_buy_point(c_sig, 5)
        if not sig:
            sig = self.buy_point(c_sig, 5)
        return sig

    def find_out_signal(self, c_sig: Signal):
        sig = self.common_out(c_sig, timeout=20)
        if not sig:
            sig = self.out(c_sig)
        return sig

    def find_sell_signal(self, c_sig: Signal, b_sig: Signal):
        sig = self.common_sell_point(c_sig, b_sig)
        if not sig:
            sig = self.sell_point(c_sig, b_sig)
        return sig

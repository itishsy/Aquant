from engines.engine import strategy_engine, Engine
from models.signal import Signal
from strategies.uab import Uab
from datetime import datetime, timedelta


@strategy_engine
class U60(Engine, Uab):

    def find_choice_signal(self, code):
        sig = self.search(code=code, freq=60, mfreq=60, mrate=0.8)
        if sig and sig.dt > (datetime.now() - timedelta(days=20)).strftime('%Y-%m-%d'):
            sig.type = 'diver-bottom'
            return sig

    def find_buy_signal(self, c_sig: Signal):
        sig = self.common_buy_signal(c_sig, 15)
        if not sig:
            return self.buy_signal(c_sig, 15)
        return sig

    def find_out_signal(self, c_sig: Signal):
        sig = self.common_out(c_sig, timeout=20)
        if not sig:
            return self.out(c_sig)
        return sig

    def find_sell_signal(self, c_sig: Signal, b_sig: Signal):
        sig = self.common_sell_signal(c_sig, b_sig)
        if not sig:
            sig = self.sell_signal(c_sig, b_sig)
        return sig

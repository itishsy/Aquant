from engines.engine import strategy_engine, Engine
from models.signal import Signal
from strategies.ma import MA20
from datetime import datetime, timedelta


@strategy_engine
class U20(Engine, MA20):

    def find_choice_signal(self, code):
        sig = self.search(code)
        if sig and sig.dt > (datetime.now() - timedelta(days=10)).strftime('%Y-%m-%d'):
            sig.type = 'diver-bottom'
            return sig

    def find_out_signal(self, c_sig: Signal):
        sig = self.common_out(c_sig, timeout=10)
        if not sig:
            return self.out(c_sig)
        return sig

    def find_buy_signal(self, c_sig: Signal):
        sig = self.watch(c_sig.code, t=-1)
        return sig

    def find_sell_signal(self, c_sig: Signal, b_sig: Signal):
        sig = self.watch(c_sig.code, t=1)
        return sig

from engines.engine import strategy_engine, Engine
from models.signal import Signal
from models.ticket import Ticket
from strategies.ma import MA20, MA60
from datetime import datetime, timedelta


@strategy_engine
class Upward(Engine):

    def find_choice_signal(self, code):
        sig = MA20.search(code)
        if sig and sig.dt > (datetime.now() - timedelta(days=10)).strftime('%Y-%m-%d'):
            sig.type = 'diver-bottom'
            return sig
        sig = MA60.search(code)
        if sig and sig.dt > (datetime.now() - timedelta(days=15)).strftime('%Y-%m-%d'):
            sig.type = 'diver-bottom'
            return sig


    def find_bs_point(self, ti: Ticket):
        return

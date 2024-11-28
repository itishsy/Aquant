from engines.base import BaseSearcher, strategy_engine
from models.signal import Signal
from models.symbol import Symbol
from models.choice import Choice
from strategies.ma import MA20, MA60
from datetime import datetime, timedelta


@strategy_engine
class U20(BaseSearcher):

    def search(self, code):
        sig = MA20.search(code)
        if sig and sig.dt > (datetime.now() - timedelta(days=10)).strftime('%Y-%m-%d'):
            sig.type = 'diver-bottom'
            return sig


@strategy_engine
class U10(BaseSearcher):

    def search(self, code):
        sig = MA20.search(code)
        if sig and sig.dt > (datetime.now() - timedelta(days=10)).strftime('%Y-%m-%d'):
            sig.type = 'diver-bottom'
            return sig


@strategy_engine
class U60(BaseSearcher):

    def search(self, code):
        sig = MA20.search(code)
        if sig and sig.dt > (datetime.now() - timedelta(days=10)).strftime('%Y-%m-%d'):
            sig.type = 'diver-bottom'
            return sig

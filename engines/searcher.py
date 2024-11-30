from engines.engine import Searcher, job_engine
from models.signal import Signal
from models.symbol import Symbol
from models.choice import Choice
from strategies.ma20 import MA20
from datetime import datetime, timedelta


@job_engine
class U20(Searcher):

    def search(self, code):
        sig = MA20.search(code)
        if sig and sig.dt > (datetime.now() - timedelta(days=5)).strftime('%Y-%m-%d'):
            sig.type = 'diver-bottom'
            return sig


@job_engine
class U10(Searcher):

    def search(self, code):
        sig = MA20.search(code)
        if sig and sig.dt > (datetime.now() - timedelta(days=10)).strftime('%Y-%m-%d'):
            sig.type = 'diver-bottom'
            return sig


@job_engine
class B103(Searcher):

    def search(self, code):
        sig = MA20.search(code)
        if sig and sig.dt > (datetime.now() - timedelta(days=10)).strftime('%Y-%m-%d'):
            sig.type = 'diver-bottom'
            return sig

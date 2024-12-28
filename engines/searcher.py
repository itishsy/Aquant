from engines.engine import Searcher, job_engine
from candles.storage import find_candles
from strategies.ma10 import MA10
from strategies.ma20 import MA20
from strategies.ma60 import MA60
from datetime import datetime, timedelta


@job_engine
class U20(Searcher):

    def search(self, code):
        sig = MA20.search(code)
        sig.stage = 'choice'
        sig.notify = 0
        return sig


@job_engine
class U60(Searcher):

    def search(self, code):
        sig = MA60.search(code)
        sig.stage = 'choice'
        sig.notify = None
        return sig


@job_engine
class U10(Searcher):

    def search(self, code):
        return MA10.search(code)

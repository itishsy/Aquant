from engines.engine import Searcher, job_engine
from candles.storage import find_candles
from strategies.ma10 import MA10
from strategies.ma20 import MA20
from strategies.ma60 import MA60
from datetime import datetime, timedelta


@job_engine
class U20(Searcher):

    def search(self, code):
        return MA20.search(code)


@job_engine
class U60(Searcher):

    def search(self, code):
        return MA60.search(code)


@job_engine
class U10(Searcher):

    def search(self, code):
        return MA10.search(code)

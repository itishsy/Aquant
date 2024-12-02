from engines.engine import Searcher, job_engine
from candles.storage import find_candles
from strategies.ma20 import MA20
from strategies.ma60 import MA60
from datetime import datetime, timedelta
from candles.finance import fetch_data
from candles.marker import mark
from signals.divergence import diver_bottom


@job_engine
class U20(Searcher):

    def search(self, code):
        sig = MA20.search(code)
        if sig:
            begin = datetime.strptime(sig.dt, '%Y-%m-%d')
            cds = find_candles(code, freq=101, begin=begin)
            if len(cds) < 5:
                sig.type = 'diver-bottom'
                return sig


@job_engine
class U60(Searcher):

    def search(self, code):
        sig = MA60.search(code)
        if sig:
            begin = datetime.strptime(sig.dt, '%Y-%m-%d')
            cds = find_candles(code, freq=101, begin=begin)
            if len(cds) < 10:
                candles15 = fetch_data(code, 15, begin=begin)
                candles15 = mark(candles15)
                dbs = diver_bottom(candles15)
                if len(dbs) > 0:
                    sig15 = dbs[-1].dt
                    sig15.type = 'diver-bottom'
                    return sig15


@job_engine
class B103(Searcher):

    def search(self, code):
        sig = MA20.search(code)
        if sig and sig.dt > (datetime.now() - timedelta(days=10)).strftime('%Y-%m-%d'):
            sig.type = 'diver-bottom'
            return sig

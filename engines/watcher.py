from engines.engine import Watcher, job_engine
from candles.finance import fetch_data
from candles.marker import mark
from signals.divergence import diver_top, diver_bottom


@job_engine
class B5(Watcher):

    def watch(self, code):
        candles = fetch_data(code, 5)
        candles = mark(candles)
        dbs = diver_bottom(candles)
        if len(dbs) > 0:
            return dbs[-1]


@job_engine
class B15(Watcher):

    def watch(self, code):
        candles = fetch_data(code, 15)
        candles = mark(candles)
        dbs = diver_bottom(candles)
        if len(dbs) > 0:
            return dbs[-1]


@job_engine
class S5(Watcher):

    def watch(self, code):
        candles = fetch_data(code, 5)
        candles = mark(candles)
        dts = diver_top(candles)
        if len(dts) > 0:
            return dts[-1]


@job_engine
class S15(Watcher):

    def watch(self, code):
        candles = fetch_data(code, 15)
        candles = mark(candles)
        dts = diver_top(candles)
        if len(dts) > 0:
            return dts[-1]

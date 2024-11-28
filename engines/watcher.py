from engines.engine import BaseWatcher, job_engine
from candles.fetcher import fetch_data
from candles.marker import mark
from signals.divergence import diver_top, diver_bottom


@job_engine
class Watcher(BaseWatcher):

    def watch(self, code, freq):
        candles = fetch_data(code, freq)
        candles = mark(candles)
        dbs = diver_bottom(candles)
        if len(dbs) > 0:
            return dbs[-1]
        dts = diver_top(candles)
        if len(dts) > 0:
            return dts[-1]

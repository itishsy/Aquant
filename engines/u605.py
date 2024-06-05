from engines.engine import strategy_engine, Engine
from candles.storage import find_candles
from signals.divergence import diver_bottom, diver_top


@strategy_engine
class U663(Engine):
    """
      appear 60/30 bottom divergence in ma60 upward trend
    """
    def search(self, code):
        candles = find_candles(code)

        if not self.common_filter(candles):
            return

        last_30s = candles[-30:]
        idx = 0
        for c in last_30s:
            if c.ma60 <= c.close:
                idx = idx + 1

        if idx < 27:
            return

        dts = diver_top(candles)
        if len(dts) > 0:
            return

        c60 = find_candles(code, freq=60)
        d60 = diver_top(c60)
        if len(d60) > 0:
            return

        dbs = diver_bottom(c60)
        if len(dbs) > 0:
            return dbs[-1]

    def watch(self, cho):
        pass

    def deal(self, tic):
        pass

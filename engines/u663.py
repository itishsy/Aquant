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
        last_60s = candles[-60:]
        idx = 0
        for c in last_60s:
            if c.ma60 <= c.close:
                idx = idx + 1

        if idx < 55:
            return

        dts = diver_top(candles)
        if len(dts) > 0:
            return

        c60 = find_candles(code, freq=60)
        dbs = diver_bottom(c60)
        if len(dbs) > 0:
            return dbs[-1]
        else:
            c30 = find_candles(code, freq=30)
            dbs = diver_bottom(c30)
            if len(dbs) > 0:
                return dbs[-1]

    def watch(self, cho):
        pass

    def deal(self, tic):
        pass

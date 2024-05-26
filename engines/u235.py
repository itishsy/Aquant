from engines.engine import strategy_engine, Engine
from candles.storage import find_candles
from signals.divergence import diver_bottom, diver_top


@strategy_engine
class U235(Engine):
    """
      appear 30/15min bottom divergence in ma20 upward trend
    """
    def search(self, code):
        candles = find_candles(code)

        if not self.common_filter(candles):
            return

        last_50s = candles[-50:]
        idx = 0
        for c in last_50s:
            if c.ma20 <= c.close:
                idx = idx + 1

        if idx < 40:
            return

        dts = diver_top(candles)
        if len(dts) > 0:
            return

        c30 = find_candles(code, freq=30)
        dbs = diver_bottom(c30)
        if len(dbs) > 0:
            return dbs[-1]
        else:
            c15 = find_candles(code, freq=15)
            dbs = diver_bottom(c15)
            if len(dbs) > 0:
                return dbs[-1]

    def watch(self, cho):
        pass

    def deal(self, tic):
        pass

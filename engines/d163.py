from engines.engine import strategy_engine, Engine
from candles.storage import find_candles
from signals.divergence import diver_bottom, diver_top


@strategy_engine
class D163(Engine):
    """
      appear 30/60 bottom divergence after 101 bottom divergence
    """
    def search(self, code):
        candles = find_candles(code)
        size = len(candles)
        if size < 100:
            return

        dbs = diver_bottom(candles)
        if len(dbs) > 0:
            sig = dbs[-1]
            sub_candles = find_candles(code, freq=60, begin=sig.dt)
            sub_abs = diver_bottom(sub_candles)
            if len(sub_abs) > 0:
                return sub_abs[-1]
            else:
                sub_candles = find_candles(code, freq=30, begin=sig.dt)
                sub_abs = diver_bottom(sub_candles)
                if len(sub_abs) > 0:
                    return sub_abs[-1]

    def watch(self, cho):
        pass

    def deal(self, tic):
        pass

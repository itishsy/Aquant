from engines.engine import strategy_engine, Engine
from candles.storage import find_candles
from signals.divergence import diver_bottom, diver_top


@strategy_engine
class U663(Engine):
    """
      appear 60/30 bottom divergence in ma60 upward trend
    """
    def search(self, code):
        pass

    def watch(self, cho):
        pass

    def deal(self, tic):
        pass

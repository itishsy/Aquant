from engines.engine import strategy_engine, Engine
from candles.storage import find_candles
from signals.divergence import diver_bottom, diver_top


@strategy_engine
class U235(Engine):
    """
      appear 30/15min bottom divergence in ma20 upward trend
    """
    def search(self, code):
        pass

    def watch(self, cho):
        pass

    def deal(self, tic):
        pass

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

        if not self.common_filter(candles):
            return

        dts = diver_top(candles)
        if len(dts) > 0:
            return

        dbs = diver_bottom(candles)
        if len(dbs) > 0:
            s1 = dbs[-1]
            sub_candles = find_candles(code, freq=60, begin=s1.dt)
            sub_abs = diver_bottom(sub_candles)
            if len(sub_abs) > 0:
                s6 = sub_abs[-1]
                if s6.price > s1.price:
                    sub_dts = diver_top(sub_candles)
                    if len(sub_dts) > 0:
                        return
                    else:
                        return s6
            else:
                sub_candles = find_candles(code, freq=30, begin=s1.dt)
                sub_abs = diver_bottom(sub_candles)
                if len(sub_abs) > 0:
                    s3 = sub_abs[-1]
                    if s3.price > s1.price:
                        sub_dts = diver_top(sub_candles)
                        if len(sub_dts) > 0:
                            return
                        else:
                            s3.strategy = 'd163'
                            return s3

    def watch(self, cho):
        pass

    def deal(self, tic):
        pass

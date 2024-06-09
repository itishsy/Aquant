from engines.engine import strategy_engine, Engine
from candles.storage import find_candles
from signals.divergence import diver_bottom, diver_top
from models.signal import Signal


@strategy_engine
class U630(Engine):
    """
      appear 60/30 bottom divergence in ma60 upward trend
    """
    def search(self, code):
        candles = find_candles(code)

        if not self.common_filter(candles):
            return

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
        sig = Signal.get(Signal.id == cho.sid)
        if sig:
            dt = sig.dt
            price = sig.price
            freq = sig.freq
            if freq == 30:
                cs5 = self.fetch_candles(code=cho.code, freq=5, begin=dt)
                db5 = diver_bottom(cs5)
                if len(db5) > 0 and db5[-1].price > price:
                    return db5[-1]
            elif freq == 60:
                cs15 = self.fetch_candles(code=cho.code, freq=15, begin=dt)
                db15 = diver_bottom(cs15)
                if len(db15) > 0 and db15[-1].price > price:
                    return db15[-1]
                cs10 = self.fetch_candles(code=cho.code, freq=10, begin=dt)
                db10 = diver_bottom(cs10)
                if len(db10) > 0 and db10[-1].price > price:
                    return db10[-1]

    def deal(self, tic):
        pass

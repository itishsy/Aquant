from candles.storage import find_candles
from signals.divergence import diver_bottom
import signals.utils as utl


class Drc:
    def __int__(self, code, freq=101, c_freq=30):
        self.code = code
        self.freq = freq
        self.c_freq = 30

    def search(self):
        candles = find_candles(self.code)
        size = len(candles)

        # 至少100根
        if size < 100:
            return

        dbs = diver_bottom(candles)
        if len(dbs) == 0:
            return

        # 最后一个背离signal
        s1 = dbs[-1]
        sec = utl.get_section(candles, s1.dt)
        for c in sec:
            if c.low < s1.price:
                return

        candles2 = find_candles(self.code, self.c_freq, begin=s1.dt)
        dbs2 = diver_bottom(candles2)
        if len(dbs2) == 0:
            return

        s2 = dbs2[-1]
        sec2 = utl.get_section(candles2, s2.dt)
        for c2 in sec2:
            if c2.low < s2.price:
                return

        return s2

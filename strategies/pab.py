from candles.storage import find_candles
import signals.utils as utl
from signals.divergence import diver_bottom


class Pab:

    def __int__(self, code, freq=30):
        self.code = code
        self.freq = freq

    def search(self):
        candles = find_candles(self.code)
        size = len(candles)

        # 至少100根
        if size < 100:
            return

        # 当前段在0轴上方
        s_last = utl.get_stage(candles, candles[-1].dt)
        for c in s_last:
            if c.diff() < 0 or c.dea9 < 0:
                return

        # 符合金叉-下叉形态
        crs = utl.get_cross(candles)
        if crs[-1].mark != 1:
            return

        cross0 = crs[-2:][0]
        if cross0.mark == -1 and cross0.diff() > 0 and cross0.dea9 > 0:
            print('last golden above 0 axis')
            # 底背离
            cds = find_candles(self.code, freq=self.freq, begin=cross0.dt)
            dbs = diver_bottom(cds)
            if len(dbs) > 0:
                return dbs[-1]

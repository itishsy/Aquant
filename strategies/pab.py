from candles.storage import find_candles
import signals.utils as utl
from signals.divergence import diver_bottom


class Pab:
    def __int__(self, freq, code):
        self.freq = freq
        self.code = code

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

    def out(self, c_sig, timeout=None):
        cds = find_candles(self.code, begin=c_sig.dt)

        if timeout and len(cds) > timeout:
            sig = c_sig
            sig.dt = cds[-1].dt
            sig.type = 'timeout'
            return sig

        for cd in cds:
            if cd.low < c_sig.price:
                sig = c_sig
                sig.dt = cd.dt
                sig.type = 'damage-lowest'
                return sig
            if cd.dea9 < 0 and cd.diff() < 0:
                sig = c_sig
                sig.dt = cd.dt
                sig.type = 'damage-axis'
                return sig

    def sell_point(self):



from candles.storage import find_candles
import signals.utils as utl
from signals.divergence import diver_bottom, diver_top
import candles.fetcher as fet
import candles.marker as mar
from models.signal import Signal


class Pab:

    @staticmethod
    def search(code, freq):
        candles = find_candles(code)
        size = len(candles)

        # 至少100根
        if size < 100:
            return

        # 当前段在0轴上方
        s_last = utl.get_stage(candles, candles[-1].dt)
        for c in s_last:
            if c.diff() < 0 or c.dea9 < 0:
                return

        dts = diver_top(candles)
        if len(dts) > 0:
            return

        # 符合金叉-下叉形态
        crs = utl.get_cross(candles)
        if len(crs) < 3 or crs[0].diff() < 0 or crs[0].dea9 < 0 or crs[1].diff() < 0 or crs[1].dea9 < 0:
            return

        # cross0 = crs[-2:][0]
        # if cross0.mark == -1 and cross0.diff() > 0 and cross0.dea9 > 0:
        # 底背离
        cds = find_candles(code, freq=freq)
        dbs = diver_bottom(cds)
        if len(dbs) > 0:
            sig = dbs[-1]
            for cd in candles:
                if cd.dt > sig.dt and cd.low < sig.price:
                    return
            return sig

    @staticmethod
    def buy_signal(c_sig: Signal, b_freq):
        pass

    @staticmethod
    def sell_signal(c_sig: Signal, b_sig: Signal):
        pass

    @staticmethod
    def out(c_sig):
        cds = find_candles(c_sig.code, begin=c_sig.dt)
        for cd in cds:
            if cd.dea9 < 0 and cd.diff() < 0:
                sig = c_sig
                sig.dt = cd.dt
                sig.type = 'damage-axis'
                return sig

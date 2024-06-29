from candles.storage import find_candles
import signals.utils as utl
from signals.divergence import diver_bottom, diver_top
import candles.fetcher as fet
import candles.marker as mar
from models.signal import Signal


class Uab:

    @staticmethod
    def search(code, freq, mfreq=None, mrate=0.7):
        if mfreq is None:
            mfreq = freq

        candles = find_candles(code)
        size = len(candles)

        # 至少100根
        if size < 100:
            return

        # 在ma上线占比
        lcs = candles[-mfreq:]
        idx = 0
        for c in lcs:
            ma = eval('c.ma'+str(mfreq))
            if ma <= c.close:
                idx = idx + 1
        if idx/mfreq < mrate:
            return

        # 调整幅度不可过大（最近M根最高最低与当前收盘价比较）
        highest = utl.get_highest(lcs)
        lowest = utl.get_lowest(lcs)
        # stage_lowest = utl.get_lowest(utl.get_stage(candles, candles[-1].dt))
        if (highest.high - candles[-1].close) / (highest.high - lowest.low) < 0.618:
            return

        # 不可出现量价背离（最高点的那根：阴线或长上影线，收盘不是最高，成交量最大，且远高于平均成高量的）
        v_highest = utl.get_highest_volume(lcs)
        c_highest = utl.get_highest_close(lcs)
        if v_highest.dt == highest.dt and c_highest.dt != highest.dt and highest.close < highest.open:
            bts = utl.get_between(candles, c_highest.dt, 5, 10)
            avg = utl.get_average_volume(bts)
            if avg/highest.volume < 0.6:
                return

        # 不可出现顶背离
        dts = diver_top(candles)
        if len(dts) > 0:
            return

        # 底背离
        cds = find_candles(code, freq=freq, begin=highest.dt)
        dbs = diver_bottom(cds)
        if len(dbs) == 0:
            return

        sig = dbs[-1]
        sec = utl.get_section(cds, sig.dt, candles[-1].dt)
        sec_lowest = utl.get_lowest(sec)
        if sec_lowest.dt == sig.dt:
            return sig

    @staticmethod
    def buy_point(c_sig: Signal, b_freq):
        pass

    @staticmethod
    def sell_point(c_sig: Signal, b_sig: Signal):
        pass

    @staticmethod
    def out(c_sig, timeout=None):
        cds = find_candles(c_sig.code, begin=c_sig.dt)

        if timeout and len(cds) > timeout:
            sig = c_sig
            sig.dt = cds[-1].dt
            sig.type = 'timeout'
            return sig

        cds = find_candles(cho.code, begin=sig30.dt)
        # 超时不出b_signal
        if len(cds) > 10:
            return Signal(code=cho.code, name=cho.name, freq=sig30.freq, dt=cds[-1].dt, type='timeout')
        # c_signal破坏
        lowest = utl.get_lowest(cds)
        if lowest and lowest.low < sig30.price:
            return Signal(code=cho.code, name=cho.name, freq=sig30.freq, dt=cds[-1].dt, type='damage')



from candles.storage import find_candles
import signals.utils as utl
from signals.divergence import diver_bottom, diver_top


class UAB:

    def __int__(self, code, ma=30, ma_rate=0.7, freq=30):
        self.code = code
        self.ma = ma
        self.ma_rate = ma_rate
        self.freq = freq

    def search(self):
        candles = find_candles(self.code)
        size = len(candles)

        # 至少100根
        if size < 100:
            return

        # 在ma上线占比
        lcs = candles[-self.ma:]
        idx = 0
        for c in lcs:
            ma = eval(format('c.ma{}', str(self.ma)))
            if ma <= c.close:
                idx = idx + 1
        if idx/self.ma < self.ma_rate:
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
            avg = utl.get_average_volume(lcs)
            if avg/highest.volume < 0.8:
                return

        # 不可出现顶背离
        dts = diver_top(candles)
        if len(dts) > 0:
            return

        # 底背离
        cds = find_candles(self.code, freq=self.freq, begin=highest.dt)
        dbs = diver_bottom(cds)
        if len(dbs) == 0:
            return

        sig = dbs[-1]
        sec = utl.get_section(cds, sig.dt, candles[-1].dt)
        sec_lowest = utl.get_lowest(sec)
        if sec_lowest.low > sig.price:
            return sig

from models.symbol import Symbol
import strategies.utils as utl


class MA10:

    @staticmethod
    def search(code):
        candles = utl.choices(code, 10)

        if not candles:
            return

        if candles[-1].close > candles[-1].ma10:
            return

        if not utl.is_beyond_ma(candles, 10):
            return

        # 活跃度
        if not utl.is_active(candles, zhang_ting=0.085, zhang_ting_size=1):
            return

        # 高位放量
        if utl.is_top_volume(candles, pre_ratio=0.9, nxt_ratio=0.9):
            return

        # 6天内出现60min顶背离
        if utl.is_top_divergence(code, 60, limit=30):
            return

        # 3天内出现30min顶背离
        if utl.is_top_divergence(code, 30, utl.cal_limit(30, 3)):
            return

        # 1天内发出5min底背离信号
        sig = utl.driver_bottom_signal(code, 5, utl.cal_limit(5, 1))
        if sig:
            sig.notify = 0
            return sig
        else:
            sym = Symbol.get(Symbol.code == code)
            sym.is_watch = 1
            sym.save()

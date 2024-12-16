from models.symbol import Symbol
import strategies.utils as sul


class MA10:

    @staticmethod
    def search(code):
        candles = sul.choices(code, 10)

        if not candles:
            return

        if candles[-1].close > candles[-1].ma10:
            return

        if not sul.is_beyond_ma(candles, 10):
            return

        # 活跃度
        if not sul.is_active(candles, zhang_ting=0.085, zhang_ting_size=1):
            return

        # 高位放量
        if sul.is_top_volume(candles, pre_ratio=0.9, nxt_ratio=0.9):
            return

        # 6天内出现60min顶背离
        if sul.is_top_divergence(code, 60, limit=30):
            return

        # 3天内出现30min顶背离
        if sul.is_top_divergence(code, 30, 24):
            return

        # 1天内发出5min底背离信号
        sig = sul.driver_bottom_signal(code, 5, 90)
        if sig:
            sig.notify = 0
            return sig
        else:
            sym = Symbol.get(Symbol.code == code)
            sym.is_watch = 1
            sym.save()

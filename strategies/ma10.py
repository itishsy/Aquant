from models.symbol import Symbol
import strategies.utils as sul


class MA10:

    @staticmethod
    def search(code):
        candles = sul.choices(code, 20)

        if not candles:
            return

        if not sul.is_beyond_ma(candles, 10, ma_ratio=0.85):
            return

        # 活跃度
        if not sul.is_active(candles, zhang_ting_size=1):
            return

        # 高位放量
        if sul.is_top_volume(candles):
            return

        sym = Symbol.get(Symbol.code == code)
        sym.is_watch = 1
        sym.save()

        # 半天内发出5min底背离信号
        sig = sul.driver_bottom_signal(code, 5, 48)
        if sig:
            sig.notify = 0
            return sig

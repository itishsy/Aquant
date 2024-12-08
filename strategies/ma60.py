from models.symbol import Symbol
import strategies.utils as sul


class MA60:

    @staticmethod
    def search(code):
        candles = sul.choices(code, 30)

        if not candles:
            return

        # 在ma60线之上
        if not sul.is_beyond_ma(candles, 60, ma_ratio=0.9):
            return

        # 活跃度不足
        if not sul.is_active(candles):
            return

        # 出现顶背离
        if sul.is_top_divergence(code, [101, 120]):
            return

        # 高位放量
        if sul.is_top_volume(candles, pre_ratio=0.7, nxt_ratio=0.7):
            return

        # 大A形态
        if sul.is_big_a(candles, down_ratio=0.618):
            return

        # 5天内发出的60min底背离信号
        sig = sul.driver_bottom_signal(code, 60, 20)
        if not sig:
            # 3天内发出的15min底背离信号
            sig = sul.driver_bottom_signal(code, 30, 24)

        if sig:
            return sig
        else:
            sym = Symbol.get(Symbol.code == code)
            sym.is_watch = 1
            sym.save()
        # else:
        #     return Signal(code=code, freq=60, dt=candles[-1].dt, price=candles[-1].close, type='upward')



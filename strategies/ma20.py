import datetime

from models.symbol import Symbol
import strategies.utils as sul


class MA20:

    @staticmethod
    def search(code):
        candles = sul.choices(code, 20)

        if not candles:
            return

        # 在ma20线之上
        if not sul.is_beyond_ma(candles, 20, ma_ratio=0.9):
            return

        # 活跃度不足
        if not sul.is_active(candles):
            return

        # 出现顶背离
        if sul.is_top_divergence(code, [101, 120, 60]):
            return

        # 高位放量
        if sul.is_top_volume(candles, pre_ratio=0.8, nxt_ratio=0.9):
            return

        # 大A形态
        if sul.is_big_a(candles, down_ratio=0.618):
            return

        # 3天内发出30min底背离信号
        sig = sul.driver_bottom_signal(code, 30, 32)
        if not sig:
            # 2.5天内发出15min底背离信号
            sig = sul.driver_bottom_signal(code, 15, 40)

        if sig:
            sig.notify = 0
            return sig
        # else:
        #     sym = Symbol.get(Symbol.code == code)
        #     sym.is_watch = 1
        #     sym.save()
        #     return Signal(code=code, freq=20, dt=candles[-1].dt, price=candles[-1].close, type='upward')


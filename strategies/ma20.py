import datetime

from models.symbol import Symbol
import strategies.utils as utl


class MA20:

    @staticmethod
    def search(code):
        candles = utl.choices(code, 20)

        if not candles:
            return

        # 在ma20线之上
        if not utl.is_beyond_ma(candles, 20, ma_ratio=0.9):
            return

        # 活跃度不足
        if not utl.is_active(candles):
            return

        # 出现顶背离
        if utl.is_top_divergence(code, 101):
            return

        if utl.is_top_divergence(code, 60, limit=20):
            return

        # 高位放量
        if utl.is_top_volume(candles, pre_ratio=0.8, nxt_ratio=0.9):
            return

        # 大A形态
        if utl.is_big_a(candles, down_ratio=0.618):
            return

        # 5天内发出30min底背离信号
        sig = utl.driver_bottom_signal(code, 30, utl.cal_limit(30, 5))
        if not sig:
            # 2.5天内发出15min底背离信号
            sig = utl.driver_bottom_signal(code, 15, utl.cal_limit(15, 3))

        return sig

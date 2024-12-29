import strategies.utils as utl


class MA60:

    @staticmethod
    def search(code):
        candles = utl.choices(code, 30)

        if not candles:
            return

        # 在ma60线之上
        if not utl.is_beyond_ma(candles, 60, ma_ratio=0.9):
            return

        # 活跃度不足
        if not utl.is_active(candles):
            return

        # 出现顶背离
        if utl.is_top_divergence(code, 101):
            return

        # 高位放量
        if utl.is_top_volume(candles, pre_ratio=0.8, nxt_ratio=0.8):
            return

        # 大A形态
        if utl.is_big_a(candles, down_ratio=0.618):
            return

        # 15天内发出的60min底背离信号
        sig = utl.driver_bottom_signal(code, 60, utl.cal_limit(60, 15))
        if not sig:
            # 8天内发出的30min底背离信号
            sig = utl.driver_bottom_signal(code, 30, utl.cal_limit(30, 8))

        return sig

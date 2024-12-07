from candles.storage import find_candles
from signals.divergence import diver_bottom, diver_top, driver_bottom_plus
from candles.finance import fetch_data
from candles.marker import mark
from strategies.utils import choices, is_active, is_top_volume, is_top_divergence, is_beyond_ma, is_big_a


class MA20:

    @staticmethod
    def search(code):
        candles = choices(code, 20)

        if not candles:
            return

        # 在ma20线之上
        if not is_beyond_ma(candles, 20, ma_ratio=0.9):
            return

        # 活跃度不足
        if not is_active(candles):
            return

        # 出现顶背离
        if is_top_divergence(code, [101, 120, 60]):
            return

        # 高位放量
        if is_top_volume(candles, pre_ratio=0.8, nxt_ratio=0.9):
            return

        # 大A形态
        if is_big_a(candles, down_ratio=0.618):
            return

        # 15/30min底背离
        cds = find_candles(code, freq=30)
        dbs = diver_bottom(cds)
        if len(dbs) > 0:
            sig = driver_bottom_plus(dbs[-1], cds)
            if sig:
                sig.code = code
                return sig

        cds = fetch_data(code, 15)
        cds = mark(cds)
        dbs = diver_bottom(cds)
        if len(dbs) > 0:
            sig = driver_bottom_plus(dbs[-1], cds)
            if sig:
                sig.code = code
                return sig


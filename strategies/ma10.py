from candles.storage import find_candles
import signals.utils as utl
from signals.divergence import diver_bottom, diver_top, driver_bottom_plus
from candles.finance import fetch_data
from candles.marker import mark
from models.signal import Signal
from strategies.utils import choices, is_active, is_top_volume, is_beyond_ma


class MA10:

    @staticmethod
    def search(code):
        candles = choices(code, 20)

        if not candles:
            return

        if not is_beyond_ma(candles, 10, ma_ratio=0.9):
            return

        # 活跃度
        if not is_active(candles, zhang_ting_size=1):
            return

        # 高位放量
        if is_top_volume(candles):
            return

        return Signal(freq=10, dt=candles[-1].dt, price=candles[-1].close)


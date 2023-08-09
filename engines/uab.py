from engines.engine import register_engine, Engine
from storage.dba import freqs, find_stage_candles, find_candles
import signals.utils as sig
from models.signal import Signal
from datetime import datetime, timedelta
from decimal import Decimal
from signals.divergence import diver_bottom
from storage.candle import Candle
from typing import List


@register_engine
class UAB15(Engine):

    def get_freq(self):
        return 15

    def get_strategy(self):
        return 'UAB'

    def do_search(self) -> Signal:
        pass

    def find_sell_signal(self) -> Signal:
        pass

    def find_buy_point(self) -> Signal:
        pass

    def find_sell_point(self) -> Signal:
        pass

    def is_kick(self) -> bool:
        pass

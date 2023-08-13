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
class PAB(Engine):
    def search(self, code) -> List[Signal]:
        candles = find_candles(code, 30)

        pass

    def watch(self) -> Signal:
        pass

    def flush(self):
        pass

    def deal(self) -> Signal:
        pass

    def hold(self) -> Signal:
        pass
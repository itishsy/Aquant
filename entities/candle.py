from decimal import Decimal
from dataclasses import dataclass


@dataclass
class Candle:
    def __init__(self, series=None):
        if series is not None:
            for key in series.keys():
                setattr(self, key, series[key])

    id: int
    dt: str
    klt: int
    open: Decimal
    close: Decimal
    high: Decimal
    low: Decimal
    volume: Decimal = None
    turnover: Decimal = None
    ema5: Decimal = None
    ema12: Decimal = None
    ema26: Decimal = None
    dea9: Decimal = None
    czsc_mark: int = 0
    macd_mark: int = 0

    def diff(self):
        return self.ema12 - self.ema26

    def bar(self):
        return self.diff() - self.dea9

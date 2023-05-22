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
    freq: int
    open: Decimal
    close: Decimal
    high: Decimal
    low: Decimal
    volume: Decimal = None
    turnover: Decimal = None
    ma5: Decimal = None
    ma10: Decimal = None
    ma20: Decimal = None
    ma30: Decimal = None
    mav5: Decimal = None
    ema12: Decimal = None
    ema26: Decimal = None
    dea9: Decimal = None
    mark: int = 0

    def diff(self):
        return self.ema12 - self.ema26

    def bar(self):
        return self.diff() - self.dea9

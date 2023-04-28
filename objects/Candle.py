from dataclasses import dataclass


@dataclass
class Candle:

    def __init__(self, series=None):
        for key in series.keys():
            setattr(self, key, series[key])

    symbol: str
    dt: str
    klt: int
    open: float
    close: float
    high: float
    low: float
    vol: float
    ma5: float
    ma10: float
    ma20: float
    ema12: float
    ema26: float
    dea9: float
    mark: int = 0

    def diff(self):
        return self.ema12 - self.ema26

    def bar(self):
        return self.diff() - self.dea9
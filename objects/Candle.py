from dataclasses import dataclass


@dataclass
class Candle:
    symbol: str
    dt: str
    klt: int
    open: float
    close: float
    high: float
    low: float
    vol: float
    ema12: float
    ema26: float
    dea9: float
    mark: int = 0

    def diff(self):
        return self.ema12 - self.ema26

    def bar(self):
        return self.diff() - self.dea9

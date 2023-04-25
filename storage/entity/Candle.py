from dataclasses import dataclass
from datetime import datetime
from enums import Freq


@dataclass
class Candle:
    symbol: str
    id: int  # id 必须是升序
    dt: datetime
    freq: Freq
    open: [float, int]
    close: [float, int]
    high: [float, int]
    low: [float, int]
    vol: [float, int]
    amount: [float, int] = None


    @property
    def upper(self):
        """上影"""
        return self.high - max(self.open, self.close)

    @property
    def lower(self):
        """下影"""
        return min(self.open, self.close) - self.low

    @property
    def solid(self):
        """实体"""
        return abs(self.open - self.close)

    @property
    def include(self):
        """包含/被包含的序号，0-未包含，-1被前一根包含，2包含后两根"""
        return 0
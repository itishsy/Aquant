from dataclasses import dataclass
from datetime import datetime
from enums import Freq


@dataclass
class Candle:
    id: int  # id 必须是升序
    symbol: str
    dt: datetime
    freq: Freq
    open: float
    close: float
    high: float
    low: float
    vol: float
    amount: float = None
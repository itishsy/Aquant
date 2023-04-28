from dataclasses import dataclass
from datetime import datetime
from enums import Strategy


@dataclass
class Signal:
    code: str
    dt: datetime
    strategy: Strategy
    value: float = 0.0

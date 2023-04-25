from dataclasses import dataclass
from datetime import datetime


@dataclass
class Signal:
    code: str
    dt: datetime
    value: float = 0.0

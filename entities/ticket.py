from decimal import Decimal
from dataclasses import dataclass
from datetime import datetime


@dataclass
class Ticket:
    def __init__(self, code, dt, freq):
        self.code = code
        self.dt = dt
        self.freq = freq

    id: int
    code: str
    freq: int
    type: int
    dt: str
    status: int
    created: datetime = datetime.now()
    updated: datetime = None

from decimal import Decimal
from dataclasses import dataclass
from datetime import datetime
from sqlalchemy import select, desc, and_, text
from typing import List



@dataclass
class Trade:
    def __init__(self, code, dt, freq):
        self.code = code
        self.dt = dt
        self.freq = freq

    id: int
    code: str
    freq: int
    dt: str
    trade_status: int
    trade_type: int
    trade_price: Decimal
    trade_time: datetime
    notify: int
    created: datetime = datetime.now()
    updated: datetime = None


def update_trade(mappings):
    pass
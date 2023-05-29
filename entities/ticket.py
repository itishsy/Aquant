from decimal import Decimal
from dataclasses import dataclass
from datetime import datetime


@dataclass
class Ticket:
    def __init__(self, code):
        self.code = code

    id: int
    code: str
    freq: str
    type: int
    dt: str
    status: int
    created: datetime = datetime.now()
    updated: datetime = None

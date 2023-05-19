from decimal import Decimal
from dataclasses import dataclass
from datetime import datetime


@dataclass
class Ticket:

    id: int
    code: str
    type: int
    klt: int
    dt: str
    status: int
    created: datetime = datetime.now()
    updated: datetime = None

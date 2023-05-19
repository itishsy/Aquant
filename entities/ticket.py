from decimal import Decimal
from dataclasses import dataclass
from datetime import datetime


@dataclass
class Ticket:

    id: int
    code: str
    deal_type: int
    deal_klt: int
    deal_dt: str
    status: int
    updated: datetime = datetime.now()
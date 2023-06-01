from decimal import Decimal
from dataclasses import dataclass
from datetime import datetime
from models.base import BaseModel, db
from peewee import CharField, BooleanField, IntegerField, DateTimeField, DecimalField



@dataclass
class Trade2:
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


# 票据
class Trade(BaseModel):
    code = CharField()  # 票据
    freq = CharField()  # 交易级别
    dt = CharField()  # 交易时间
    strategy = CharField()  # 策略
    type = IntegerField()  # 类别 0 buy 1 sell
    status = IntegerField(default=0)  # 状态 0 未成交 1 已成交
    price = DecimalField()  # 价格
    notify = IntegerField(default=0)  # 通知 0 未通知， 1 已通知
    created = DateTimeField()
    updated = DateTimeField()


if __name__ == '__main__':
    db.connect()
    db.create_tables([Trade])
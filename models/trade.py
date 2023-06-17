from decimal import Decimal
from dataclasses import dataclass
from datetime import datetime
from models.base import BaseModel, db
from flask_peewee.db import CharField, BooleanField, IntegerField, DateTimeField, DecimalField


# 交易
class Trade(BaseModel):
    code = CharField()  # 票据
    name = CharField()  # 名称
    type = IntegerField()  # 交易类别 0 buy 1 sell
    freq = CharField()  # 交易级别
    dt = CharField()  # 交易时间
    price = DecimalField()  # 成交价
    volume = IntegerField()  # 成交量
    fee = DecimalField()  # 手续费
    status = IntegerField(default=1)  # 状态 0 无效 1 有效
    created = DateTimeField()
    updated = DateTimeField()


if __name__ == '__main__':
    db.connect()
    db.create_tables([Trade])
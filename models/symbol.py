from models.base import BaseModel, db
from flask_peewee.db import CharField, IntegerField, FloatField, DateTimeField
from datetime import datetime
import efinance as ef


class Symbol(BaseModel):
    code = CharField()  # 票据
    name = CharField()  # 名称
    status = IntegerField()  # 状态
    profit = FloatField()
    total = FloatField()
    circulating = FloatField()
    industry = FloatField()
    pe = FloatField()
    pb = FloatField()
    roe = FloatField()
    gross = FloatField()
    net = FloatField()
    sector = CharField()
    is_watch = IntegerField()
    created = DateTimeField()
    updated = DateTimeField()
    comment = CharField()

    @staticmethod
    def actives():
        return Symbol.select().where(Symbol.status == 1)


if __name__ == '__main__':
    db.connect()
    db.create_tables([Symbol])



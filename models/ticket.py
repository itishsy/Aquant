from models.signal import Signal
from models.choice import Choice
from models.base import BaseModel, db
from flask_peewee.db import CharField, AutoField, IntegerField, DateTimeField, DecimalField
from datetime import datetime


# 票据
class Ticket(BaseModel):
    id = AutoField()
    code = CharField()  # 编码
    name = CharField()  # 名称
    comment = CharField()  # 备注
    status = IntegerField(default=1)  # 状态 1 0
    created = DateTimeField()
    updated = DateTimeField()

    @staticmethod
    def add_by_choice(cho: Choice):
        if cho.bid and not Ticket.select().where(Ticket.cid == cho.id, Ticket.bid == cho.bid).exists():
            tic = Ticket()
            tic.status = Ticket.Status.PENDING
            tic.code = cho.code
            tic.name = cho.name
            tic.cid = cho.cid
            tic.bid = cho.bid
            bs = Signal.get(Signal.id == cho.bid)
            tic.sl_price = bs.price
            tic.created = datetime.now()
            tic.updated = datetime.now()
            tic.save()

    class Status:
        MISS = 0
        PENDING = 1
        TRADING = 2
        SOLD = 3

        @staticmethod
        def all():
            return [(Ticket.Status.MISS, '未交易'), (Ticket.Status.PENDING, '待买入'),
                    (Ticket.Status.TRADING, '交易中'), (Ticket.Status.SOLD, '完成交易')]

        @staticmethod
        def get(key):
            if key == Ticket.Status.MISS:
                return '未交易'
            if key == Ticket.Status.PENDING:
                return '待买入'
            if key == Ticket.Status.TRADING:
                return '交易中'
            if key == Ticket.Status.SOLD:
                return '完成交易'

#
# class TicketSignal(BaseModel):
#     tid = IntegerField()
#     sid = IntegerField()
#     created = DateTimeField()


if __name__ == '__main__':
    db.connect()
    db.create_tables([Ticket])

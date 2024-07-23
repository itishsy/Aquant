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
    status = IntegerField(default=1)  # 状态 1 待交易， 2. 交易中， 0. 交易失败， 3. 完成交易
    cid = IntegerField()  # choice signal id
    bid = IntegerField()  # buy signal id
    sid = IntegerField()  # sell signal id
    b_dt = CharField()  # 买入时间
    b_price = DecimalField()  # 买入价
    s_dt = CharField()  # 卖出时间
    s_price = DecimalField()  # 卖出价
    hold = IntegerField()  # 持有量
    sl_price = DecimalField()  # 止损价
    created = DateTimeField()
    updated = DateTimeField()

    def add_by_choice(self, cho: Choice):
        if not Ticket.select().where(Ticket.cid == cho.id, Ticket.bid == cho.bid).exists():
            self.status = 1
            self.code = cho.code
            self.name = cho.name
            self.cid = cho.id
            self.bid = cho.bid
            bs = Signal.get(Signal.id == cho.bid)
            self.sl_price = bs.price
            self.created = datetime.now()
            self.updated = datetime.now()
            self.save()

    class Status:
        UNEXECUTED = 0
        PENDING = 1
        TRADING = 2
        SOLD = 3

        @staticmethod
        def all():
            return [(Ticket.Status.UNEXECUTED, '未交易'), (Ticket.Status.PENDING, '待买入'),
                    (Ticket.Status.TRADING, '交易中'), (Ticket.Status.SOLD, '完成交易')]

        @staticmethod
        def get(key):
            if key == Ticket.Status.UNEXECUTED:
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

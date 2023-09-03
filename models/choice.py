from models.base import BaseModel, db
from models.signal import Signal
from flask_peewee.db import CharField, IntegerField, DateTimeField, AutoField
from datetime import datetime


# 入选池
class Choice(BaseModel):
    id = AutoField()
    code = CharField()  # 编码
    name = CharField()  # 名称
    source = CharField()  # 來源
    strategy = CharField()  # 策略值
    s_id = IntegerField()  # 信號ID
    s_freq = CharField()  # 級別
    s_dt = CharField()  # 信號時間
    created = DateTimeField()

    def add_by_signal(self, sig: Signal):
        self.code = sig.code
        self.name = sig.name
        self.s_id = sig.id
        self.s_freq = sig.freq
        self.s_dt = sig.dt
        self.created = datetime.now()
        self.save()


if __name__ == '__main__':
    db.connect()
    db.create_tables([Choice])

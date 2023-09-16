from models.base import BaseModel, db
from flask_peewee.db import CharField, DecimalField, IntegerField, DateTimeField, AutoField


# 信号
class Signal(BaseModel):
    id = AutoField()
    code = CharField()  # 票据
    name = CharField()  # 名称
    freq = CharField()  # 信号级别
    dt = CharField()  # 发生时间
    price = DecimalField()  # 信号价格
    type = IntegerField()  # 信號類別： 0 底背离 1 頂背离
    strength = IntegerField(null=True)
    effect = IntegerField(null=True)
    notify = IntegerField(null=True)  # 通知 0 待通知， 1 已通知
    created = DateTimeField()
    updated = DateTimeField(null=True)


class SIGNAL_TYPE:
    BOTTOM_DIVERGENCE = 0
    TOP_DIVERGENCE = 1
    TREND_SUPPORT = 2
    PLATFORM_SUPPORT = 3

    @staticmethod
    def all():
        return [(SIGNAL_TYPE.BOTTOM_DIVERGENCE, '底背離'),
                (SIGNAL_TYPE.TOP_DIVERGENCE, '頂背離'),
                (SIGNAL_TYPE.TREND_SUPPORT, '趨勢綫支撐'),
                (SIGNAL_TYPE.PLATFORM_SUPPORT, '平臺支撐')]

    @staticmethod
    def get(key):
        if key == SIGNAL_TYPE.BOTTOM_DIVERGENCE:
            return '底背離'
        if key == SIGNAL_TYPE.TOP_DIVERGENCE:
            return '頂背離'
        if key == SIGNAL_TYPE.TREND_SUPPORT:
            return '趨勢綫支撐'
        if key == SIGNAL_TYPE.PLATFORM_SUPPORT:
            return '平臺支撐'


# 信号的有效性，在产生信号后需要验证。0 無效 1 有效 2 破坏
class SIGNAL_EFFECT:
    INVALID = 0
    EFFECTIVE = 1
    DESTROY = 2

    @staticmethod
    def all():
        return [(SIGNAL_EFFECT.INVALID, '無效'),
                (SIGNAL_EFFECT.EFFECTIVE, '有效'),
                (SIGNAL_EFFECT.DESTROY, '破坏')]

    @staticmethod
    def get(key):
        if key == SIGNAL_EFFECT.INVALID:
            return '無效'
        if key == SIGNAL_EFFECT.EFFECTIVE:
            return '有效'
        if key == SIGNAL_EFFECT.DESTROY:
            return '破坏'


# 信号的强度，在信号产生时通过它的结构判断。 0 弱 1 中 2 强
class SIGNAL_STRENGTH:
    WEAK = 0
    AVERAGE = 1
    STRONG = 2

    @staticmethod
    def all():
        return [(SIGNAL_STRENGTH.WEAK, '弱'),
                (SIGNAL_STRENGTH.AVERAGE, '中'),
                (SIGNAL_STRENGTH.STRONG, '強')]

    @staticmethod
    def get(key):
        if key == SIGNAL_STRENGTH.WEAK:
            return '弱'
        if key == SIGNAL_STRENGTH.AVERAGE:
            return '中'
        if key == SIGNAL_STRENGTH.STRONG:
            return '強'


if __name__ == '__main__':
    db.connect()
    db.create_tables([Signal])

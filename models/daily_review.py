from models.base import BaseModel, db
from flask_peewee.db import CharField, IntegerField, DateTimeField


class DailyReview(BaseModel):
    dp_cjl = CharField()  # 大盘-成交量 https://www.cls.cn/finance
    dp_zdb = CharField()  # 大盘-涨跌数 https://www.cls.cn/quotation
    dp_zdt = CharField()  # 大盘-涨跌停
    dp_zj = CharField()  # 大盘-总结，财联社-A股-每日收评
    bk_top1 = CharField()   # 板块，今日流入1：https://www.cls.cn/hotPlate
    bk_top2 = CharField()   # 板块，今日流入2：
    bk_top3 = CharField()   # 板块，今日流入3
    bk_zx = CharField()     # 板块主线。财联社-盯盘-主线
    bk_fk = CharField()     # 板块主线。财联社-盯盘-风口
    zt_1b = CharField()     # 涨停。1板
    zt_2b = CharField()     # 涨停。2板
    zt_3b = CharField()     # 涨停。3板
    zt_gdb = CharField()     # 涨停。高度板
    zt_zgb = CharField()     # 涨停。最高板
    gp_hot1 = CharField()    # 热股。财联社 https://api3.cls.cn/quote/toplist
    gp_hot2 = CharField()    # 热股。淘股吧 https://www.tgb.cn/new/nrnt/toPopularityBoard
    created = DateTimeField()


if __name__ == '__main__':
    db.connect()
    db.create_tables([DailyReview])

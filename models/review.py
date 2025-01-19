from models.base import BaseModel, db
from flask_peewee.db import CharField, IntegerField, DateTimeField


class Review(BaseModel):
    pan_data = CharField()  # 大盘-数据，财联社,成交量/涨跌数/涨跌停 https://www.cls.cn/finance、 https://www.cls.cn/quotation
    pan_summary = CharField()  # 大盘-总结 财联社-A股-每日收评 https://www.cls.cn/subject/1139
    pan_focus = CharField()     # 大盘-总结 财联社-A股-焦点复盘。 https://www.cls.cn/subject/1135
    bk_in = CharField()   # 板块流入, https://www.cls.cn/hotPlate
    bk_out = CharField()   # 板块流出，https://www.cls.cn/hotPlate
    bk_ql = CharField()   # 板块潜力
    bk_fk = CharField()     # 板块风口
    gp_zt = CharField()     # 涨停。1板\2板、高度板
    gp_hot1 = CharField()    # 热股。财联社 https://api3.cls.cn/quote/toplist
    gp_hot2 = CharField()    # 热股。淘股吧 https://www.tgb.cn/new/nrnt/toPopularityBoard
    created = DateTimeField()


if __name__ == '__main__':
    db.connect()
    db.create_tables([Review])

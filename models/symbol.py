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
    created = DateTimeField()
    updated = DateTimeField()
    comment = CharField()

    @staticmethod
    def upset(code, name, series):
        if Symbol.select().where(Symbol.code == code).exists():
            symbol = Symbol.get(Symbol.code == code)
        else:
            symbol = Symbol()
            symbol.code = code
            symbol.updated = datetime.now()
        symbol.name = name
        for k in series.keys():
            val = series[k]
            if str(k).startswith('净利润'):
                symbol.profit = val if isinstance(val, float) else 0.0
            elif str(k).startswith('总市值'):
                symbol.total = val if isinstance(val, float) else 0.0
            elif str(k).startswith('流通市值'):
                symbol.circulating = val if isinstance(val, float) else 0.0
            elif str(k).startswith('所处行业'):
                symbol.industry = val
            elif str(k).startswith('市盈率'):
                symbol.pe = val if isinstance(val, float) else 0.0
            elif k == '市净率':
                symbol.pb = val if isinstance(val, float) else 0.0
            elif k == 'ROE':
                symbol.roe = val if isinstance(val, float) else 0.0
            elif k == '毛利率':
                symbol.gross = val if isinstance(val, float) else 0.0
            elif k == '净利率':
                symbol.net = val if isinstance(val, float) else 0.0
            elif k == '板块编号':
                symbol.sector = val
        if symbol.industry == '银行':
            symbol.status = 0
            symbol.comment = '银行'
        elif symbol.total < 5000000000 or symbol.circulating < 3000000000:
            symbol.status = 0
            symbol.comment = '小市值'
        else:
            symbol.status = 1
        symbol.updated = datetime.now()
        symbol.save()

    @staticmethod
    def actives():
        return Symbol.select().where(Symbol.status == 1)

    @staticmethod
    def fetch():
        df = ef.stock.get_realtime_quotes(['沪A', '深A'])
        df = df.iloc[:, 0:2]
        df.columns = ['code', 'name']
        for i, row in df.iterrows():
            if 'ST' in row['name'] or str(row['code']).startswith('688'):
                continue
            else:
                info = ef.stock.get_base_info(row['code'])
                print('upset symbol code =', row['code'], ',name =', row['name'], i)
                Symbol.upset(row['code'], row['name'], info)


if __name__ == '__main__':
    db.connect()
    db.create_tables([Symbol])



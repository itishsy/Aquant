import efinance as ef
import database as db
from datetime import datetime
import json


def stat_all():
    rq = ef.stock.get_realtime_quotes(['ETF','沪深A股','创业板'])
    engine = db.get_engine()
    rq.columns = ['code', 'name', 'zdf','price', 'high', 'low','open','zde','hsl','lb','pe','val','cje', 'zrsp','total', 'ltsz', 'hqid', 'market', 'upd','jyr']
    rq = rq[(rq['name'].str.contains('ST') == False) & (rq['code'].str.startswith('00') | rq['code'].str.startswith('51') |rq['code'].str.startswith('60') | rq['code'].str.startswith('30'))]
    rq.to_sql(name='all_realtime', con=engine, index=False, if_exists='replace')


if __name__ == '__main__':
    print('==========')
    stat_all('300059')
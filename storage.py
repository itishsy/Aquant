import datetime

import pandas as pd
from sqlalchemy import text
from sqlalchemy import create_engine
import efinance as ef

engine = create_engine('mysql+pymysql://root:root@127.0.0.1:3306/agu')


def insert(df, table_name,index=False):
    df.to_sql(name=table_name, con=engine, index=index, if_exists='append')


def query(sql):
    conn = engine.connect()
    df = pd.read_sql_query(text(sql), con=conn)
    conn.close()
    engine.dispose()
    return df


def upset_all():
    rq = ef.stock.get_realtime_quotes()
    rq.columns = ['code', 'name', 'zdf','price', 'high', 'low','open','zde','hsl','lb','pe','val','cje', 'zrsp','total', 'ltsz', 'hqid', 'market', 'upd','jyr']
    rq = rq[(rq['name'].str.contains('ST') == False) & (rq['code'].str.startswith('00') | rq['code'].str.startswith('60') | rq['code'].str.startswith('30'))]
    rq.to_sql(name='all_realtime', con=engine, index=False, if_exists='replace')


def upset(stock_code):
    table_name = 'k_{}'.format(stock_code)
    exits = query("SELECT COUNT(1) AS t FROM `information_schema`.`TABLES` WHERE `TABLE_SCHEMA` = 'agu' AND `TABLE_NAME` = '{}'".format(table_name)).at[0, 't']
    beg = '19000101'
    if exits > 0:
        beg_data = query("SELECT REPLACE(DATE_ADD(`datetime`, INTERVAL 1 DAY),'-','') AS d FROM `{}` ORDER BY `datetime` DESC LIMIT 1 ".format(table_name))
        if len(beg_data) > 0:
            beg = beg_data.at[0, 'd']

    for klt in [101, 102, 103, 60, 30, 15]:
        k_data = ef.stock.get_quote_history(stock_code, klt=klt,beg=beg)
        k_data.columns = ['name', 'code', 'datetime', 'open', 'close', 'high', 'low', 'volume', 'cje', 'zf', 'rise', 'zde', 'hsl']
        k_data.drop(['name','code'], axis=1, inplace=True)
        k_data['klt'] = klt
        insert(k_data, table_name)


"""
读取K线数据
klt : int, 默认日线。共4类
        - ``15`` : 15 分钟
        - ``60`` : 60 分钟
        - ``101`` : 日
        - ``102`` : 周
sta : str, 格式如'2023-02-01'
end : str, 格式如'2023-02-01'
"""


def read(stock_code, klt=101, beg='', end='', field='*', limit=-1, order_by='datetime'):
    table_name = 'k_{}'.format(stock_code)
    sql = 'SELECT {} FROM {} WHERE klt={}'.format(field,table_name,klt)
    if beg != '':
        sql = "{} AND `datetime` >= '{}'".format(sql,beg)
    if end != '':
        sql = "{} AND `datetime` <= '{}'".format(sql,end)
    sql = "{} ORDER BY {} ".format(sql,order_by)
    if limit > -1:
        sql = "{} LIMIT {}".format(sql,limit)
    return query(sql)


def fetch_data():
    upset_all()
    codes = query('SELECT code FROM `all_realtime`')
    t1 = datetime.datetime.now()
    for idx,row in codes.iterrows():
        print('{} upset code {}'.format(idx, row.code))
        upset(row.code)
    t2 = datetime.datetime.now()
    print('开始时间：{}, 结束时间:{} , 一共用时：{}分钟'.format(t1, t2, (t2-t1).seconds/60))


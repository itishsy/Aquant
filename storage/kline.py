import database as db
import efinance as ef

def upset_data(stock_code, begin):
    table_name = 'k_{}'.format(stock_code)
    begin = '19000101'
    beg_data = db.query("SELECT REPLACE(DATE_ADD(`datetime`, INTERVAL 1 DAY),'-','') AS d FROM `{}` ORDER BY `datetime` DESC LIMIT 1 ".format(table_name))
    if len(beg_data) > 0:
        begin = beg_data.at[0, 'd']

    for klt in [101, 102, 103, 60, 30, 15]:
        k_data = ef.stock.get_quote_history(stock_code, klt=klt, beg=begin)
        k_data.columns = ['name', 'code', 'datetime', 'open', 'close', 'high', 'low', 'volume', 'cje', 'zf', 'rise', 'zde', 'hsl']
        k_data.drop(['name','code'], axis=1, inplace=True)
        k_data['klt'] = klt
        db.insert(k_data, table_name)


def read_data(stock_code, klt=101, beg='', end='', field='*', limit=-1, order_by='datetime'):
    sql = 'SELECT {} FROM {} WHERE klt={}'.format(field, 'k_{}'.format(stock_code), klt)
    if beg != '':
        sql = "{} AND `datetime` >= '{}'".format(sql, beg)
    if end != '':
        sql = "{} AND `datetime` <= '{}'".format(sql, end)
    sql = "{} ORDER BY {} ".format(sql,order_by)
    if limit > -1:
        sql = "{} LIMIT {}".format(sql,limit)
    return db.query(sql)
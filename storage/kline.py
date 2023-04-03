import storage.database as db
from datetime import datetime
import efinance as ef


def upset_data(stock_code, begin_date):
    if begin_date == "-1":
        return -1

    size = 0
    if begin_date == "":
        db.create_stock_table(stock_code)
        db.execute("TRUNCATE TABLE `{}`".format(stock_code))
        print('[create table] name:{}'.format(stock_code))
        begin_date = '2000-01-01'
    if begin_date < datetime.now().strftime('%Y-%m-%d'):
        begin_date = begin_date.replace('-', '')
        print('[get history] code:{}, from:{}'.format(stock_code, begin_date))
        for klt in [101, 102, 103, 60, 30, 15]:
            k_data = ef.stock.get_quote_history(stock_code, klt=klt, beg=begin_date)
            data_size = len(k_data)
            if data_size > 0:
                k_data = k_data.iloc[:, 0:8]
                k_data.columns = ['name', 'code', 'datetime', 'open', 'close', 'high', 'low', 'volume']
                k_data.drop(['name', 'code'], axis=1, inplace=True)
                k_data['ema5'] = None
                k_data['ema12'] = None
                k_data['ema26'] = None
                k_data['dea4'] = None
                k_data['dea9'] = None
                k_data['klt'] = klt
                db.insert(k_data, stock_code)
                size = size + data_size
    return size


def read_data(stock_code, klt=101, begin='', end='', field='*', limit=-1, order_by='datetime'):
    sql = 'SELECT {} FROM `{}` WHERE klt={}'.format(field, stock_code, klt)
    if begin != '':
        sql = "{} AND `datetime` >= '{}'".format(sql, begin)
    if end != '':
        sql = "{} AND `datetime` <= '{}'".format(sql, end)
    sql = "{} ORDER BY {} ".format(sql, order_by)
    if limit > -1:
        sql = "{} LIMIT {}".format(sql,limit)
    return db.query(sql)


def read_mark(stock_code, klt=101, begin='', mark='-3,3'):
    sql = 'SELECT * FROM `{}` WHERE klt={} AND mark IN ({})'.format(stock_code, klt, mark)
    if begin != '':
        sql = "{} AND `datetime` >= '{}'".format(sql, begin)
    sql = "{} ORDER BY `datetime` ".format(sql)
    return db.query(sql)

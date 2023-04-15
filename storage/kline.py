import storage.database as db
from datetime import datetime
import efinance as ef
import config as cfg


def upset_data(stock_code, klt, begin_date):
    size = 0
    if begin_date.strftime('%Y-%m-%d') < datetime.now().strftime('%Y-%m-%d'):
        begin_date = begin_date.strftime('%Y%m%d')
        print('[get history] code:{}, klt:{}, from:{}'.format(stock_code, klt, begin_date))
        k_data = ef.stock.get_quote_history(stock_code, klt=klt, beg=begin_date)
        data_size = len(k_data)
        if data_size > 0:
            k_data = k_data.iloc[:, 0:8]
            k_data.columns = ['name', 'code', 'datetime', 'open', 'close', 'high', 'low', 'volume']
            # k_data.drop(['name', 'code'], axis=1, inplace=True)
            s_sql = db.get_sql('insert_kline.sql').format(stock_code, klt)
            i_list = []
            for i, row in k_data.iterrows():
                i_list.append((row['datetime'],
                               row['open'],
                               row['close'],
                               row['high'],
                               row['low'],
                               row['volume'],
                               row['datetime']))
                if len(i_list) > 100:
                    db.execute(db.get_connect(stock_code), s_sql, many=True, lis=i_list)
                    i_list.clear()
            if len(i_list) > 0:
                db.execute(db.get_connect(stock_code), s_sql, many=True, lis=i_list)
            size = size + data_size
    return size


def upset_data2(stock_code, begin_date):
    size = 0
    if begin_date.strftime('%Y-%m-%d') < datetime.now().strftime('%Y-%m-%d'):
        begin_date = begin_date.strftime('%Y%m%d')
        print('[get history] code:{}, from:{}'.format(stock_code, begin_date))
        for klt in [101, 102, 103]:
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
        sql = "{} LIMIT {}".format(sql, limit)
    return db.query(sql)


def read_mark(stock_code, klt=101, begin='', mark='-3,3'):
    sql = 'SELECT `datetime`,`open`,`close`,`high`,`low`, (`ema12`-`ema26`) AS diff, (`ema12`-`ema26`-`dea9`) AS bar,`mark`' \
          ' FROM `{}` WHERE klt={} AND mark IN ({})'.format(stock_code, klt, mark)
    if begin != '':
        sql = "{} AND `datetime` >= '{}'".format(sql, begin)
    sql = "{} ORDER BY `datetime` ".format(sql)
    return db.query(sql)


if __name__ == '__main__':
    sql = """INSERT INTO `301080`(`datetime`, `open`, `close`, `high`, `low`, `volume`, `klt`)
    SELECT '2023-04-07', 110.96, 109.99, 112.89, 105.81, 28381, 102
    FROM DUAL WHERE NOT EXISTS(
        SELECT 1
        FROM `301080`
        WHERE `datetime` = %s AND `klt` = 102
        );"""
    db.execute(db.get_connect('301080'), sql, many=True, lis=[('2023-04-07'), ('2023-04-06')])

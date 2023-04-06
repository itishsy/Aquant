import efinance as ef
import storage.database as db


def stat_all():
    rq = ef.stock.get_realtime_quotes(['ETF','沪深A股','创业板'])
    engine = db.get_engine()
    rq.columns = ['code', 'name', 'zdf','price', 'high', 'low','open','zde','hsl','lb','pe','val','cje', 'zrsp','total', 'ltsz', 'hqid', 'market', 'upd','jyr']
    rq = rq[(rq['name'].str.contains('ST') == False) & (rq['code'].str.startswith('00') | rq['code'].str.startswith('51') |rq['code'].str.startswith('60') | rq['code'].str.startswith('30'))]
    rq.to_sql(name='all_realtime', con=engine, index=False, if_exists='replace')


def fetch_error(stock_code,begin_date,error):
    insert_sql = "INSERT INTO `fetch_error` (" \
                 "`stock_code`,`begin_date`,`create`,`error`) " \
                 "VALUES('{}','{}',NOW(),'{}');"\
        .format(stock_code,begin_date,error)
    db.execute(insert_sql)


def reverse_signal(stock_code,level,type,datetime):
    delete_sql = "DELETE FROM `reverse_signal` " \
                 "WHERE `stock_code` = '{}' " \
                 "AND `level` = '{}' " \
                 "AND `reverse_datetime` = '{}'"\
        .format(stock_code,level,datetime)
    db.execute(delete_sql)
    insert_sql = "INSERT INTO `reverse_signal` " \
                 "(`stock_code`,`level`,`reverse_type`,`reverse_datetime`,`create`) " \
                 "VALUES('{}','{}','{}','{}',NOW())"\
        .format(stock_code,level,type,datetime)
    print(insert_sql)
    db.execute(insert_sql)

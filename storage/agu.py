import efinance as ef
import storage.database as db


def stat_all():
    rq = ef.stock.get_realtime_quotes(['ETF','沪深A股','创业板'])
    engine = db.get_engine()
    rq.columns = ['code', 'name', 'zdf','price', 'high', 'low','open','zde','hsl','lb','pe','val','cje', 'zrsp','total', 'ltsz', 'hqid', 'market', 'upd','jyr']
    rq = rq[(rq['name'].str.contains('ST') == False) & (rq['code'].str.startswith('00') | rq['code'].str.startswith('51') |rq['code'].str.startswith('60') | rq['code'].str.startswith('30'))]
    rq.to_sql(name='all_realtime', con=engine, index=False, if_exists='replace')



def reverse_signal(stock_code,level,type,datetime):
    delete_sql = "DELETE FROM `reverse_signal` " \
                 "WHERE `stock_code` = '{}' " \
                 "AND `level` = '{}' " \
                 "AND `reverse_datetime` = '{}'"\
        .format(stock_code,level,datetime)
    db.execute(db.get_connect(), delete_sql)
    insert_sql = "INSERT INTO `reverse_signal` " \
                 "(`stock_code`,`level`,`reverse_type`,`reverse_datetime`,`create`) " \
                 "VALUES('{}','{}','{}','{}',NOW())"\
        .format(stock_code,level,type,datetime)
    db.execute(db.get_connect(),insert_sql)


def reverse_signal2(stock_code,level,type,datetime):
    delete_sql = "DELETE FROM `reverse_signal` " \
                 "WHERE `stock_code` = '{}' " \
                 "AND `level` = '{}' " \
                 "AND `reverse_datetime` = '{}'"\
        .format(stock_code,level,datetime)
    db.execute2(delete_sql)
    insert_sql = "INSERT INTO `reverse_signal` " \
                 "(`stock_code`,`level`,`reverse_type`,`reverse_datetime`,`create`) " \
                 "VALUES('{}','{}','{}','{}',NOW())"\
        .format(stock_code,level,type,datetime)
    db.execute2(insert_sql)

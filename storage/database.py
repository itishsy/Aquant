import logging
import sqlalchemy.pool
from sqlalchemy import text
from sqlalchemy import create_engine
from sqlalchemy.types import DATE, VARCHAR, INT, DECIMAL, BIGINT
import pandas as pd
import config as cfg
from datetime import datetime, timedelta
from objects import Candle
import pymysql


def init_schema():
    db = pymysql.connect(host=cfg.host,
                         port=cfg.port,
                         user=cfg.username,
                         passwd=cfg.password,
                         database="mysql")
    execute(db, 'schema.sql')


def get_sql(sql_file):
    with open(cfg.work_path + r"//storage//sql//" + sql_file, encoding='utf-8', mode='r') as f:
        return f.read()


def get_engine(code=''):
    dbname = 'agu'
    if code[0:2] in cfg.prefix:
        dbname = 'agu_{}'.format(code[0:2])
    engine = create_engine(
        'mysql+pymysql://{0}:{1}@{2}:{3}/{4}'.format(
            cfg.username,
            cfg.password,
            cfg.host,
            cfg.port,
            dbname),
        poolclass=sqlalchemy.pool.NullPool)
    return engine


def get_connect(code=''):
    dbname = 'agu'
    if code != '' and code[0:2] in cfg.prefix:
        dbname = 'agu_{}'.format(code[0:2])
    return pymysql.connect(
        host=cfg.host,
        port=cfg.port,
        user=cfg.username,
        passwd=cfg.password,
        database=dbname
    )


def get_table_name(sql):
    sps = sql.split(' ')
    le = len(sps)
    for i in range(le):
        if (sps[i].upper() == 'FROM') | (sps[i].upper() == 'TABLE') | (sps[i].upper() == 'UPDATE') | (
                sps[i].upper() == 'INTO'):
            table_name = sps[i + 1]
            table_name = table_name.replace("`", "")
            return table_name


def insert(df, table_name, replace=False):
    mode = 'append'
    if replace:
        mode = 'replace'
    engine = get_engine(table_name)
    dtypes = get_dtypes(table_name)
    df.to_sql(name=table_name, con=engine, index=False, if_exists=mode, dtype=dtypes)


def execute(db, sql, *args, many=False, lis=None):
    cursor = db.cursor()
    args_size = len(args)
    try:
        if '.sql' in sql:
            with open(cfg.work_path + r"//storage//sql//" + sql, encoding='utf-8', mode='r') as f:
                sql_list = f.read().split(';')[:-1]
                for x in sql_list:
                    if '\n' in x:
                        # 替换空行为1个空格
                        x = x.replace('\n', ' ')

                    # 判断多个空格时
                    if '    ' in x:
                        # 替换为空
                        x = x.replace('    ', '')

                    # sql语句添加分号结尾
                    sql_item = x + ';'
                    # logging.info(sql_item)
                    for i in range(args_size):
                        a = "{" + str(i) + "}"
                        sql_item = sql_item.replace(a, str(args[i]))
                    # print(sql_item)
                    if many:
                        cursor.executemany(sql_item, lis)
                    else:
                        cursor.execute(sql_item)
                    # logging.info("执行成功sql: %s" % sql_item)
        else:
            if many:
                cursor.executemany(sql, lis)
            else:
                cursor.execute(sql)
    except Exception as e:
        print(e)
        logging.error('execute sql failed: %s' % sql)
    finally:
        # 关闭mysql连接
        cursor.close()
        db.commit()
        db.close()


# def execute2(sql):
#     engine = get_engine(get_table_name(sql))
#     with engine.connect() as conn:
#         conn.execute(text(sql))
#         conn.commit()
#     engine.dispose()


# def drop_table(table_name):
#     engine = get_engine(table_name)
#     sql = 'DROP TABLE IF EXISTS `{}`'.format(table_name)
#     conn = engine.connect()
#     conn.execute(text(sql))
#     conn.commit()
#     engine.dispose()


def query(sql):
    engine = get_engine(get_table_name(sql))
    conn = engine.connect()
    df = pd.read_sql_query(text(sql), con=conn)
    conn.close()
    engine.dispose()
    return df


def create_stock_table(code):
    if code[0:2] not in cfg.prefix:
        return
    dbname = 'agu_{}'.format(code[0:2])
    db = pymysql.connect(host=cfg.host, port=cfg.port, user=cfg.username, passwd=cfg.password, database=dbname)
    execute(db, 'create_stock.sql', code)


def get_dtypes(table_name):
    if table_name[0:2] in cfg.prefix:
        return {'datetime': VARCHAR(20), 'open': DECIMAL, 'close': DECIMAL, 'high': DECIMAL, 'low': DECIMAL,
                'volume': BIGINT, 'ema5': DECIMAL, 'ema12': DECIMAL, 'ema26': DECIMAL, 'dea4': DECIMAL, 'dea9': DECIMAL,
                'mark': INT, 'klt': INT}


def read_kline_data(stock_code, klt=101, begin='', end='', field='*', limit=-1, order_by='datetime'):
    sql = 'SELECT {} FROM `{}` WHERE klt={}'.format(field, stock_code, klt)
    if begin != '':
        sql = "{} AND `datetime` >= '{}'".format(sql, begin)
    if end != '':
        sql = "{} AND `datetime` <= '{}'".format(sql, end)
    sql = "{} ORDER BY {} ".format(sql, order_by)
    if limit > -1:
        sql = "{} LIMIT {}".format(sql, limit)
    return query(sql)


def save_signal(stock_code, klt, typ, dtime, tip=False):
    if tip:
        select_sql = "SELECT 1 FROM `watcher_detail` " \
                     "WHERE `code` = '{}' " \
                     "AND `klt` = '{}' " \
                     "AND `event_type` = '{}'" \
                     "AND `event_datetime` = '{}'" \
            .format(stock_code, klt, typ, dtime)
        df = query(select_sql)
        if len(df) == 0:
            sql = "INSERT INTO `watcher_detail` " \
                  "(`code`,`klt`,`event_type`,`event_datetime`,`created`) " \
                  "VALUES('{}','{}','{}','{}',NOW())" \
                .format(stock_code, klt, typ, dtime)
            execute(get_connect(), sql)
    else:
        select_sql = "SELECT 1 FROM `reverse_signal` " \
                     "WHERE `stock_code` = '{}' " \
                     "AND `level` = '{}' " \
                     "AND `reverse_type` = '{}'" \
                     "AND `reverse_datetime` = '{}'" \
            .format(stock_code, klt, typ, dtime)
        df = query(select_sql)
        sql = "INSERT INTO `reverse_signal` " \
              "(`stock_code`,`level`,`reverse_type`,`reverse_datetime`,`created`) " \
              "VALUES('{}','{}','{}','{}',NOW())" \
            .format(stock_code, klt, typ, dtime)
        if len(df) > 0:
            sql = "UPDATE `reverse_signal` SET `updated` = NOW() " \
                  "WHERE `stock_code` = '{}' " \
                  "AND `level` = '{}' " \
                  "AND `reverse_type` = '{}'" \
                  "AND `reverse_datetime` = '{}'".format(stock_code, klt, typ, dtime)
        execute(get_connect(), sql)


def get_begin_datetime(stock_code, klt, mark=False):
    sql = "SELECT max(`datetime`) AS dt FROM `{}` WHERE `klt`={}".format(stock_code, klt)
    if mark:
        sql = "{} AND `mark` IS NOT NULL".format(sql)
    df = query(sql)
    dt = df.loc[0, 'dt']

    if dt is None:
        dtime = cfg.get_latest(klt)
        return dtime.strftime('%Y-%m-%d')
    else:
        if klt in [101, 102]:
            dtime = datetime.strptime(dt, '%Y-%m-%d') + timedelta(days=1)
            now = datetime.now()
            if (dtime.year == now.year) and (dtime.month == now.month) and (dtime.day == now.day) and (
                    now.hour > 8) and (now.hour < 16):
                return datetime.now().strftime('%Y-%m-%d')
            else:
                return dtime.strftime('%Y-%m-%d')
        else:
            dtime = datetime.strptime(dt, '%Y-%m-%d %H:%M')
            return dtime.strftime('%Y-%m-%d')


def read_mark_data(stock_code, klt=101, begin=None, mark='*', limit=100):
    sql = 'SELECT `datetime`,`open`,`close`,`high`,`low`, (`ema12`-`ema26`) AS diff, (`ema12`-`ema26`-`dea9`) AS bar,`dea9`,`mark`' \
          ' FROM `{}` WHERE klt={}'.format(stock_code, klt)
    if mark == '*':
        sql = '{} AND `mark` IS NOT NULL'.format(sql)
    else:
        sql = '{} AND `mark` IN ({})'.format(sql, mark)
    if begin is not None:
        sql = "{} AND `datetime` >= '{}'".format(sql, begin)
    sql = "{} ORDER BY `datetime` LIMIT {}".format(sql, limit)
    return query(sql)


def read_mark_candle(stock_code, klt=101, begin=None, mark='*', limit=100):
    sql = 'SELECT `datetime`,`open`,`close`,`high`,`low`, (`ema12`-`ema26`) AS diff, (`ema12`-`ema26`-`dea9`) AS bar,`dea9`,`mark`' \
          ' FROM `{}` WHERE klt={}'.format(stock_code, klt)
    if mark == '*':
        sql = '{} AND `mark` IS NOT NULL'.format(sql)
    else:
        sql = '{} AND `mark` IN ({})'.format(sql, mark)
    if begin is not None:
        sql = "{} AND `datetime` >= '{}'".format(sql, begin)
    sql = "{} ORDER BY `datetime` LIMIT {}".format(sql, limit)
    m_data = query(sql)
    candles = []
    for i, row in m_data.iterrows():
        candles.append(Candle(row))
    return candles


if __name__ == '__main__':
    # print(get_begin_datetime('000547', 101))
    init_schema()

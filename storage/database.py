import logging
import sqlalchemy.pool
from sqlalchemy import text
from sqlalchemy import create_engine
from sqlalchemy.types import DATE, VARCHAR, INT, DECIMAL, BIGINT
import pandas as pd
import config as cfg
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


if __name__ == '__main__':
    init_schema()

from sqlalchemy import text
from sqlalchemy import create_engine
from sqlalchemy.types import DATE, VARCHAR, INT, DECIMAL, BIGINT
import pandas as pd
import json
import os


with open(os.path.abspath('.') + r"\\storage\\config.json", 'r', encoding='utf-8') as load_f:
    load_dict = json.load(load_f)
    host = load_dict['host']
    username = load_dict['username']
    password = load_dict['password']
engine_agu = create_engine('mysql+pymysql://{}:{}@{}/agu'.format(username, password, host))
engine_agu_00 = create_engine('mysql+pymysql://{}:{}@{}/agu_00'.format(username, password, host))
engine_agu_30 = create_engine('mysql+pymysql://{}:{}@{}/agu_30'.format(username, password, host))
engine_agu_51 = create_engine('mysql+pymysql://{}:{}@{}/agu_51'.format(username, password, host))
engine_agu_60 = create_engine('mysql+pymysql://{}:{}@{}/agu_60'.format(username, password, host))


def init_schema():
    dbs = query('SELECT `SCHEMA_NAME` AS name FROM `information_schema`.`SCHEMATA`')
    all_dbs = ['agu', 'agu_30', 'agu_00', 'agu_51', 'agu_60']
    for name in all_dbs:
        df = dbs[dbs['name'] == name]
        if len(df) < 1:
            create_db_sql = 'CREATE DATABASE IF NOT EXISTS {} DEFAULT CHARACTER SET utf8 DEFAULT COLLATE utf8_general_ci;'.format(name)
            execute(create_db_sql)


def get_engine(table_name=''):
    if table_name is None:
        return engine_agu
    if table_name.startswith('00'):
        return engine_agu_00
    if table_name.startswith('30'):
        return engine_agu_30
    if table_name.startswith('60'):
        return engine_agu_60
    if table_name.startswith('51'):
        return engine_agu_51
    else:
        return engine_agu


def get_table_name(sql):
    sps = sql.split(' ')
    le = len(sps)
    for i in range(le):
        if (sps[i].upper() == 'FROM') | (sps[i].upper() == 'TABLE') | (sps[i].upper() == 'UPDATE'):
            table_name = sps[i+1]
            table_name = table_name.replace("`", "")
            return table_name


def insert(df, table_name, replace=False):
    mode = 'append'
    if replace is True:
        mode = 'replace'
    engine = get_engine(table_name)
    dtypes = get_dtypes(table_name)
    df.to_sql(name=table_name, con=engine, index=False, if_exists=mode, dtype=dtypes)


def execute(sql):
    engine = get_engine(get_table_name(sql))
    conn = engine.connect()
    conn.execute(text(sql))
    conn.commit()


def query(sql):
    engine = get_engine(get_table_name(sql))
    conn = engine.connect()
    df = pd.read_sql_query(text(sql), con=conn)
    conn.close()
    engine.dispose()
    return df


def create_table(table_name):
    if table_name.startswith('00') | table_name.startswith('30') | table_name.startswith('60') | table_name.startswith('51'):
        engine = get_engine(table_name)
        conn = engine.connect()
        sql = "CREATE TABLE IF NOT EXISTS `{}` (`datetime` varchar(20)," \
              "`open` decimal(10,2),`close` decimal(10,2),`high` decimal(10,2),`low` decimal(10,2),`volume` bigint(20), `hsl` decimal(12,4)," \
              "`ema5` decimal(12,6),`ema12` decimal(12,6),`ema26` decimal(12,6),`dea4` decimal(12,6),`dea9` decimal(12,6)," \
              "`mark` int(11) DEFAULT 0,`klt` int(11) DEFAULT NULL" \
              ") ENGINE=InnoDB DEFAULT CHARSET=utf8".format(table_name)
        conn.execute(text(sql))
        conn.commit()
        engine.dispose()


def get_dtypes(table_name):
    if table_name.startswith('00') | table_name.startswith('60') | table_name.startswith('30') | table_name.startswith('51'):
        return {'datetime': VARCHAR(20), 'open': DECIMAL, 'close': DECIMAL, 'high': DECIMAL, 'low': DECIMAL,
                    'volume': BIGINT, 'ema5': DECIMAL, 'ema12': DECIMAL, 'ema26': DECIMAL, 'dea4': DECIMAL, 'dea9': DECIMAL,
                    'mark': INT, 'klt': INT}


if __name__ == '__main__':
    init_schema()

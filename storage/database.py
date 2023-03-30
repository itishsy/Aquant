from sqlalchemy import text
from sqlalchemy import create_engine
from sqlalchemy.types import DATE, CHAR, VARCHAR, INT
import efinance as ef
import pandas as pd
import json
from datetime import datetime


with open("config.json", 'r', encoding='utf-8') as load_f:
    load_dict = json.load(load_f)
    host = load_dict['host']
    username = load_dict['username']
    password = load_dict['password']
engine_agu = create_engine('mysql+pymysql://{}:{}@{}/agu'.format(username, password, host))
engine_agu_k_30 = create_engine('mysql+pymysql://{}:{}@{}/agu_k_30'.format(username, password, host))
engine_agu_i_30 = create_engine('mysql+pymysql://{}:{}@{}/agu_i_30'.format(username, password, host))
engine_agu_k_00 = create_engine('mysql+pymysql://{}:{}@{}/agu_k_00'.format(username, password, host))
engine_agu_i_00 = create_engine('mysql+pymysql://{}:{}@{}/agu_i_00'.format(username, password, host))
engine_agu_k_60 = create_engine('mysql+pymysql://{}:{}@{}/agu_k_60'.format(username, password, host))
engine_agu_i_60 = create_engine('mysql+pymysql://{}:{}@{}/agu_i_60'.format(username, password, host))


def init_code():
    with open("code.json", 'r', encoding='utf-8') as load_f:
        code_dict = json.load(load_f)
    cur_month = datetime.now().strftime('%Y%m')
    code_ud = code_dict['ud']
    if code_ud != cur_month:
        df = ef.stock.get_realtime_quotes()
        df.columns = ['code', 'name', 'zdf','price', 'high', 'low','open','zde','hsl','lb','pe','val','cje', 'zrsp','total', 'ltsz', 'hqid', 'market', 'upd','jyr']
        c00 = []
        c60 = []
        c30 = []
        c51 = []
        df = df[df['name'].str.contains('ST') == False]
        for idx, row in df.iterrows():
            code = row['code']
            if code.startswith('00'):
                c00.append(code)
            if code.startswith('60'):
                c60.append(code)
            if code.startswith('30'):
                c30.append(code)
            if code.startswith('51'):
                c51.append(code)
        code_dict['00'] = '|'.join(c00)
        code_dict['60'] = '|'.join(c60)
        code_dict['30'] = '|'.join(c30)
        code_dict['51'] = '|'.join(c51)
        code_dict['ud'] = cur_month
        with open("code.json", 'w', encoding='utf-8') as f:
            json.dump(code_dict, f, ensure_ascii=False)


def init():
    init_code()
    dbs = query('SELECT `SCHEMA_NAME` AS name FROM `information_schema`.`SCHEMATA` WHERE 1=2')
    print(dbs)
    all_dbs = ['agu', 'agu_k_30', 'agu_i_30', 'agu_k_00', 'agu_i_00', 'agu_k_60', 'agu_i_60']
    for name in all_dbs:
        df = dbs[dbs['name'] == name]
        if len(df) < 1:
            create_sql = 'CREATE DATABASE IF NOT EXISTS {} DEFAULT CHARACTER SET utf8 DEFAULT COLLATE utf8_general_ci;'.format(name)
            execute(create_sql)


def get_engine(table_name='s_all'):
    if table_name is None:
        return engine_agu

    if table_name.find('_') > 0:
        dbtype=table_name.split('_')[0]
        prefix=table_name.split('_')[1]
        if dbtype == 'k':
            if prefix.startswith('00'):
                return engine_agu_k_00
            elif prefix.startswith('60'):
                return engine_agu_k_60
            elif prefix.startswith('30'):
                return engine_agu_k_30
        elif dbtype == 'i':
            if prefix.startswith('00'):
                return engine_agu_i_00
            elif prefix.startswith('60'):
                return engine_agu_i_60
            elif prefix.startswith('30'):
                return engine_agu_i_30
    return engine_agu


def get_table_name(sql):
    sps = sql.split(' ')
    le = len(sps)
    for i in range(le):
        if (sps[i].upper() == 'FROM') | (sps[i].upper() == 'TABLE'):
            table_name = sps[i+1]
            table_name = table_name.replace("`", "")
            return table_name


def insert(df, table_name):
    engine = get_engine(table_name)
    df.to_sql(name=table_name, con=engine, index=False, if_exists='append')


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


def create(table_name):
    if table_name.startswith('k_'):
        create_k = '''CREATE TABLE IF NOT EXISTS `{}` (
                  `datetime` text,
                  `open` text,
                  `close` text,
                  `high` text,
                  `low` text,
                  `volume` text,
                  `cje` text,
                  `zf` text,
                  `rise` text,
                  `zde` text,
                  `hsl` text,
                  `klt` bigint(20) DEFAULT NULL
                ) ENGINE=InnoDB DEFAULT CHARSET=utf8'''.format(table_name)
        engine = get_engine(table_name)
        conn = engine.connect()
        conn.execute(text(create_k))
        conn.commit()
        engine.dispose()


def get_dtypes(table_name):
    if table_name.startswith('k_'):
        dtypes_k = {'datetime': CHAR(16), 'open': CHAR(4), 'col_3': VARCHAR(10)}
        return dtypes_k


if __name__ == '__main__':
    print('====== database init ======')
    init()

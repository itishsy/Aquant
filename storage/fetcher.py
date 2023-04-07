from datetime import datetime,timedelta
from storage.kline import upset_data
import storage.database as db
import storage.indicator as idc
import config as cfg
import efinance as ef
import json


def init_code_dict():
    df = db.query("SELECT COUNT(1) AS c FROM `code_dict`")
    c = df.iloc[0, df.columns.get_loc('c')]
    if c == 0:
        df = ef.stock.get_realtime_quotes(['沪A', '深A', 'ETF'])
        df = df.iloc[:, 0:2]
        df.columns = ['code', 'name']
        df = df[df['name'].str.contains('ST') == False]
        for idx, row in df.iterrows():
            code = row['code']
            if (code[0:2] in cfg.prefix):
                db.execute("INSERT INTO `code_dict` (`code`, `created`) VALUES ('{}', NOW());".format(code))


def fetch_code_dict():
    df = db.query("SELECT `code` FROM `code_dict` WHERE `latest` = 0")
    return df


def update_storage_date(code, val=None):
    db.execute("UPDATE `code_dict` SET `updated` = NOW() WHERE `code` = '{}'".format(code))


def last_storage_date(code):
    df = db.query("SELECT `updated` FROM `code_dict` WHERE `code` = '{}'".format(code))

    if len(df) == 0:
        db.drop_table(code)
        return "-1"

    updated = df.iloc[0, df.columns.get_loc('updated')]
    if updated is None:
        db.drop_table(code)
        db.create_stock_table(code)
        last_date = datetime((datetime.now().year - 3), 1, 1)
        print('[create table] name:{}'.format(code))
        return last_date
    else:
        return updated


def fetch_data(code):
    begin_date = last_storage_date(code)
    print(code, begin_date)
    if (begin_date != '-1') and (begin_date.strftime('%Y-%m-%d') < datetime.now().strftime('%Y-%m-%d')):
        fetch_size = upset_data(code, begin_date)
        print("[updated] code:{}, begin:{}, result:{}".format(code, begin_date, fetch_size))
        if fetch_size > 0:
            idc.macd_mark(code, 101, begin_date)
            idc.macd_mark(code, 102, begin_date)
            update_storage_date(code)
    else:
        print("code:{} is up to date".format(code))
    return begin_date


if __name__ == '__main__':
    init_code_dict()
    #print('fetch_data(300223)')
    #fetch_data('300223')

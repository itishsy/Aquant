from datetime import datetime,timedelta

import config
import storage.kline as kl
import storage.database as db
import storage.indicator as ic
from strategy.macd_signal import signal
import config as cfg
import efinance as ef
import logging


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
    db.execute(db.get_connect(), "UPDATE `code_dict` SET `updated` = NOW() WHERE `code` = '{}'".format(code))

def update_storage_date2(code, val=None):
    db.execute2("UPDATE `code_dict` SET `updated` = NOW() WHERE `code` = '{}'".format(code))



def last_storage_date(code):
    df = db.query("SELECT `updated` FROM `code_dict` WHERE `code` = '{}'".format(code))

    if len(df) == 0:
        return "-1"

    updated = df.iloc[0, df.columns.get_loc('updated')]
    if updated is None:
        db.drop_table(code)
        db.create_stock_table(code)
        last_date = datetime((datetime.now().year - 3), 1, 1)
        logging.info('[create table] name:{}'.format(code))
        return last_date
    else:
        return updated


def fetch_data(code):
    begin_date = last_storage_date(code)
    if (begin_date != '-1') and (begin_date.strftime('%Y-%m-%d') < datetime.now().strftime('%Y-%m-%d')):
        fetch_size = kl.upset_data(code, begin_date)
        logging.info("[updated] code:{}, begin:{}, result:{}".format(code, begin_date, fetch_size))
        if fetch_size > 0:
            ic.macd_mark(code, 101, begin_date)
            ic.macd_mark(code, 102, begin_date)
    else:
        logging.info("code:{} is up to date".format(code))


def fetch_data2(code):
    begin_date = last_storage_date(code)
    if (begin_date != '-1') and (begin_date.strftime('%Y-%m-%d') < datetime.now().strftime('%Y-%m-%d')):
        fetch_size = kl.upset_data2(code, begin_date)
        logging.info("[updated] code:{}, begin:{}, result:{}".format(code, begin_date, fetch_size))
        if fetch_size > 0:
            ic.macd_mark2(code, 101, begin_date)
            ic.macd_mark2(code, 102, begin_date)
    else:
        logging.info("code:{} is up to date".format(code))


if __name__ == '__main__':
    #init_code_dict()
    #print('fetch_data(300223)')
    fetch_data('300059')


def fetch_all():
    code_dict = db.query("SELECT `code`,`updated` FROM `code_dict` WHERE `latest` = 0")
    for klt in config.klt:
        for i, row in code_dict.iterrows():
            code = row['code']
            begin_date = row['updated']
            try:
                if begin_date is None:
                    db.create_stock_table(code)
                    begin_date = config.get_latest(klt)
                if begin_date < datetime.now():
                    res = kl.upset_data(code, begin_date)
                    if res > 0:
                        mark_size = ic.mark(code, klt, begin_date)
                        if mark_size > 0:
                            signal(code, klt, begin_date)
            except Exception as e:
                logging.error('{} fetch {} error: {}'.format(i, code, e))
            else:
                now = datetime.now()
                updated = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                if now.hour > 15:
                    updated = datetime.now().strftime('%Y-%m-%d 23:59:59')
                db.execute(db.get_connect(), "UPDATE `code_dict` SET `updated` = '{}' WHERE `code` = '{}'".format(updated, code))


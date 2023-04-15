import storage.database as db
import storage.fetcher as fet
import storage.indicator as ind
from datetime import datetime
import logging
import traceback
import config as cfg


def watch_all():
    code_dict = db.query("SELECT `code`, `klt`  FROM `watcher` WHERE `status` = 1")
    for i, row in code_dict.iterrows():
        code = row['code']
        for klt in [120, 60, 30, 15]:
            try:
                fet.fetch_kline_data(code, klt)
                ind.update_mark(code, klt)
            except Exception as e:
                traceback.print_exc()
                logging.error('{} fetch {} error: {}'.format(i, code, e))
            else:
                ind.save_signal(code, klt)

def read_send_data():
    send_data = db.query("SELECT `code`, `klt`, `last_reverse_bottom`, `last_reverse_top`, `last_macd_balance`, `last_bottom`, `last_top` FROM `watcher` WHERE `status` = 1 AND `to_send` = 1")
    msg = ''
    if len(send_data) > 0:
        for i, row in send_data.iterrows():
            msg = '{}; index: {}, code: {}, klt: {}, reverse_bottom: {}'.format(msg, i, row['code'], row['klt'], row['last_reverse_bottom'])
    return msg


def update_send_status():
    up_sql = 'UPDATE `watcher` SET `to_send` = 0'
    db.execute(db.get_connect(),up_sql)

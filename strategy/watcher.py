import storage.database as db
import storage.fetcher as fet
import storage.indicator as ind
from datetime import datetime, timedelta
import logging
import traceback
import time


def watch_all():
    code_dict = db.query("SELECT `code`, `watch_klt`  FROM `watcher` WHERE `status` = 1")
    for i, row in code_dict.iterrows():
        code = row['code']
        wkl = row['watch_klt'].split(',')
        for klt in wkl:
            klt = int(klt)
            try:
                fet.fetch_kline_data(code, klt)
                ind.update_mark(code, klt)
            except Exception as e:
                traceback.print_exc()
                logging.error('{} fetch {} error: {}'.format(i, code, e))
            else:
                ind.save_signal(code, klt, watch=True)


def read_send_data():
    dtime = (datetime.now() - timedelta(days=2)).strftime('%Y-%m-%d')
    send_data = db.query(
        "SELECT `code`, `klt`, `event_type`, `event_datetime` FROM `watcher_detail` WHERE `notify` = 0 AND `event_datetime` > '{}'".format(
            dtime))
    msg = ''
    if len(send_data) > 0:
        for i, row in send_data.iterrows():
            msg = '【{}】, klt: {}, type: {}, datetime: {}; {}' \
                .format(row['code'], row['klt'], row['event_type'], row['event_datetime'], msg)
    return msg


def update_notify():
    up_sql = 'UPDATE `watcher_detail` SET `notify` = 1'
    db.execute(db.get_connect(), up_sql)


if __name__ == '__main__':
    while True:
        try:
            watch_all()
        except:
            pass
        finally:
            while True:
                if (datetime.now().hour > 15) or (datetime.now().hour < 9):
                    time.sleep(1800)
                else:
                    break
            time.sleep(600)

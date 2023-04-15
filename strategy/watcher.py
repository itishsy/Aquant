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
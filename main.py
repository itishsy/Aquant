from datetime import datetime
from storage.fetcher import fetch_data
from storage.db import find_active_symbols
from signals.strategy import StrategyFactory
import logging
import config
import time

logging.basicConfig(format='%(asctime)s %(message)s', filename='d://aquant.log'.format(config.work_path))
logging.getLogger().setLevel(logging.INFO)


def fetch_all():
    sbs = find_active_symbols()
    for sb in sbs:
        try:
            fetch_data(sb.code, 102)
            fetch_data(sb.code, 101)
            fetch_data(sb.code, 60)
        except:
            logging.error('{} error'.format(sb.code))


def watch_start():
    while True:
        try:
            now = datetime.now()
            wd = now.weekday() + 1
            hm = now.hour * 100 + now.minute
            if wd in [1, 2, 3, 4, 5]:
                if hm in [946, 1001, 1016, 1031, 1046, 1101, 1116, 1131,
                          1316, 1331, 1346, 1401, 1416, 1431, 1446, 1501, 2226]:
                    print("start watching. {} {} {}".format(datetime.now().strftime('%Y-%m-%d'), wd, hm))
                    fetch_signals()
                    print('watch all done!')
                elif hm in [1601, 1602, 2001, 2002]:
                    print("start fetching. {} {} {}".format(datetime.now().strftime('%Y-%m-%d'), wd, hm))
                    fetch_signals()
                    print('fetch all done!')
        except:
            pass
        finally:
            time.sleep(60)


if __name__ == '__main__':
    start_time = datetime.now()
    fetch_all()
    sf = StrategyFactory()
    sf.search_all_signal()
    end_time = datetime.now()
    print("==============用時：{}=================".format(end_time - start_time))

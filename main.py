from datetime import datetime
from storage.fetcher import fetch_all
from signals import *
import logging
import config
import time

logging.basicConfig(format='%(asctime)s %(message)s', filename='d://aquant.log'.format(config.work_path))
logging.getLogger().setLevel(logging.INFO)


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
                    fetch_all()
                    print('watch all done!')
                elif hm in [1601, 1602, 2001, 2002]:
                    print("start fetching. {} {} {}".format(datetime.now().strftime('%Y-%m-%d'), wd, hm))
                    fetch_all()
                    print('fetch all done!')
        except:
            pass
        finally:
            time.sleep(60)


if __name__ == '__main__':
    start_time = datetime.now()
    # fetch_all()
    for name in strategy.factory:
        print('============',name)
        strategy = strategy.factory[name]()
        strategy.klt(101)
        strategy.search_all()
    end_time = datetime.now()
    print("==============用時：{}=================".format(end_time - start_time))

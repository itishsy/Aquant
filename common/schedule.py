from datetime import datetime
from storage.fetcher import fetch_all
from strategies.watcher import watch_all
from strategies.searcher import search_all
from strategies.watcher import flush_all
import time


def now_val():
    now = datetime.now()
    hm = now.hour * 100 + now.minute
    return hm


def is_trade_day():
    now = datetime.now()
    return now.weekday() < 5


def daily_task():
    while True:
        try:
            if is_trade_day():
                print('[{}] daily task running ...'.format(datetime.now()))
                nv = now_val()
                if 930 < nv < 1530:
                    print('[{}] watching ...'.format(datetime.now()))
                    watch_all()
                elif 1600 < nv < 1800:
                    print('[{}] fetching ...'.format(datetime.now()))
                    fetch_all()
                elif 1800 < nv < 2000:
                    print('[{}] searching ...'.format(datetime.now()))
                    search_all()
                elif 2100 < nv < 2300:
                    print('[{}] flushing ...'.format(datetime.now()))
                    flush_all()
        except Exception as e:
            print(e)
        finally:
            if is_trade_day():
                time.sleep(100)
            else:
                time.sleep(60 * 60 * 3)


if __name__ == '__main__':
    daily_task()

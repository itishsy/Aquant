from datetime import datetime
from storage.fetcher import fetch_all
from strategies.watcher import watch_all
from strategies.searcher import search_all
from strategies.watcher import flush_all
from notify.sender import do_send
from models.component import Component
import time


def now_val():
    now = datetime.now()
    hm = now.hour * 100 + now.minute
    return hm


def is_trade_day():
    now = datetime.now()
    return now.weekday() < 5


def is_trade_time():
    return is_trade_day() and 930 < now_val() < 1510


def no_done_today(comp):
    fet = Component.get(Component.name == comp)
    return fet.run_end.day < datetime.now().day


def daily_task():
    while True:
        try:
            print('[{}] daily task running ...'.format(datetime.now()))
            Component.update(status=1, clock_time=datetime.now()).execute()
            if is_trade_day():
                nv = now_val()
                if 930 < nv < 1530:
                    watch_all()
                elif 1600 < nv < 1800 and no_done_today('fetcher'):
                    fetch_all()
                elif 1800 < nv < 2000 and no_done_today('searcher'):
                    search_all()
                elif 2100 < nv < 2300 and no_done_today('flusher'):
                    flush_all()
            do_send()
        except Exception as e:
            print(e)
        finally:
            if is_trade_day():
                if is_trade_time():
                    time.sleep(60 * 5)
                else:
                    time.sleep(60 * 60)
            else:
                time.sleep(60 * 60 * 3)


if __name__ == '__main__':
    daily_task()

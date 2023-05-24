from datetime import datetime
from storage.fetcher import fetch_all
from strategies import *
from storage.db import find_signals
import logging
import config
import time

logging.basicConfig(format='%(asctime)s %(message)s', filename='d://aquant.log'.format(config.work_path))
logging.getLogger().setLevel(logging.INFO)


def daily_task(sta=False):
    print('[{}] daily task working'.format(datetime.now()))
    while True:
        now = datetime.now()
        try:
            if sta or (now.weekday() < 5 and (
                    (now.hour == 11 and now.minute == 40) or (now.hour == 15 and now.minute == 10))):
                fetch_all()
                search_all()
                sta=False
                print("==============用時：{}=================".format(datetime.now() - now))
                print(find_signals(begin=now.strftime('%Y-%m-%d')))
        except Exception as e:
            print(e)
        finally:
            if now.minute == 1:
                print('[{}] daily task working'.format(now))
            time.sleep(60)


def search_all(sta=None):
    if sta is None:
        for name in strategy.factory:
            st = strategy.factory[name]()
            st.search_all()
    else:
        st = strategy.factory[sta]()
        # st.freq = 60
        # st.codes = ['002419']
        st.search_all()


if __name__ == '__main__':
    daily_task(sta=True)
    # search_all('MAR')

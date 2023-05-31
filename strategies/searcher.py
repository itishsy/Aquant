from datetime import datetime
from strategies import *
import time


def daily_search():
    print('[{}] daily search working'.format(datetime.now()))
    while True:
        now = datetime.now()
        try:
            if now.weekday() < 5 and now.hour == 17 and now.minute == 10:
                search_all()
                print("==============用時：{}=================".format(datetime.now() - now))
        except Exception as e:
            print(e)
        finally:
            if now.minute == 1:
                print('[{}] daily search working'.format(now))
            time.sleep(60)


def search_all(sta=None):
    if sta is None:
        for name in strategy.factory:
            st = strategy.factory[name]()
            st.search_all()
    else:
        st = strategy.factory[sta]()
        # st.freq = 60
        # st.codes = ['603790']
        st.search_all()


if __name__ == '__main__':
    # daily_search()
    search_all()

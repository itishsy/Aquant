from datetime import datetime
from strategies import *
from models.component import Component
import time


def daily_search():
    print('[{}] searcher start ...'.format(datetime.now()))
    while True:
        now = datetime.now()
        Component.update(status=1, clock_time=datetime.now()).where(Component.name == 'searcher').execute()
        try:
            if now.weekday() < 5 and now.hour > 17 and not Component.select().where(Component.name == 'fetcher',
                                                                                    Component.status == 2).exists():
                sea = Component.get(Component.name == 'searcher')
                if sea.run_end.day < now.day or sea.run_end.hour < 17:
                    search_all()
                    print("==============用時：{}=================".format(datetime.now() - now))
        except Exception as e:
            print(e)
        finally:
            time.sleep(60 * 30)


def search_all(sta=None):
    try:
        Component.update(status=2, run_start=datetime.now()).where(Component.name == 'searcher').execute()
        if sta is None:
            for name in strategy.factory:
                st = strategy.factory[name]()
                st.search_all()
        else:
            st = strategy.factory[sta]()
            # st.freq = 60
            # st.codes = ['603790']
            st.search_all()
        Component.update(status=1, run_end=datetime.now()).where(Component.name == 'searcher').execute()
    except Exception as e:
        print(e)


if __name__ == '__main__':
    daily_search()
    # search_all()

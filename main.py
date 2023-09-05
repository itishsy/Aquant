from datetime import datetime
from storage.fetcher import fetch_all
from engines import *
import logging
import time

logging.basicConfig(format='%(asctime)s %(message)s', filename='d://aquant.log')
logging.getLogger().setLevel(logging.INFO)

#
# def fetch_and_search_all(sta=False):
#     try:
#         now = datetime.now()
#         fetch_all()
#         search_all()
#         print("==============用時：{}=================".format(datetime.now() - now))
#     except Exception as e:
#         print(e)

#
# def search_all(sta=None):
#     if sta is None:
#         for name in strategy.factory:
#             st = strategy.factory[name]()
#             st.search_all()
#     else:
#         st = strategy.factory[sta]()
#         # st.freq = 60
#         st.code = '000802'
#         st.search_all()


if __name__ == '__main__':
    while True:
        for name in engine.strategy:
            st = engine.strategy[name]()
            st.start()
        print("engine working：{}".format(datetime.now()))
        time.sleep(60 * 10)


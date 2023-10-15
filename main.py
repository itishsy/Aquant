from datetime import datetime
from engines import *
import logging
import time

logging.basicConfig(format='%(asctime)s %(message)s', filename='d://aquant.log')
logging.getLogger().setLevel(logging.INFO)


if __name__ == '__main__':
    while True:
        for name in engine.strategy:
            st = engine.strategy[name]()
            print("[{}] {} start...".format(datetime.now(), name))
            st.start()
        print("[{}] sleep {} min".format(datetime.now(), 5))
        time.sleep(60 * 5)


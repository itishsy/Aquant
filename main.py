from datetime import datetime
from engines import *
from models.component import Component
import logging
import time
from notify.qywx import Qywx

logging.basicConfig(format='%(asctime)s %(message)s', filename='d://aquant.log')
logging.getLogger().setLevel(logging.INFO)


if __name__ == '__main__':
    qywx = Qywx()
    qywx.send('start')
    while True:
        Component.update(run_start=datetime.now(), status=Component.Status.RUNNING).where(
            Component.name == 'engine').execute()
        for name in engine.strategy:
            st = engine.strategy[name]()
            print("[{}] {} start...".format(datetime.now(), name))
            st.start()
        print("[{}] sleep {} min".format(datetime.now(), 5))
        Component.update(run_start=datetime.now(), status=Component.Status.READY).where(
            Component.name == 'engine').execute()
        qywx.find_signal_and_send()
        time.sleep(60 * 5)


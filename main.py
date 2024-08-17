from datetime import datetime
from engines import *
from models.component import Component
import logging
import time
import threading
from notify.notify import Notify
import os
from app import create_app

logging.basicConfig(format='%(asctime)s %(message)s', filename='d://aquant.log')
logging.getLogger().setLevel(logging.INFO)


class EngineTask(threading.Thread):
    def run(self):
        notify = Notify()
        while True:
            Component.update(run_start=datetime.now(), status=Component.Status.RUNNING).where(
                Component.name == 'engine').execute()
            for name in engine.strategy:
                st = engine.strategy[name]()
                print("[{}] {} start...".format(datetime.now(), name))
                st.start()
            Component.update(run_start=datetime.now(), status=Component.Status.READY).where(
                Component.name == 'engine').execute()
            notify.do_send()
            print("[{}] sleep {} min".format(datetime.now(), 5))
            time.sleep(60 * 5)


# et = EngineTask()
# et.start()

if __name__ == '__main__':
    et = EngineTask()
    et.start()
    app = create_app(os.getenv('FLASK_CONFIG') or 'default')
    app.run(port=5000, host='172.172.4.101', debug=False)



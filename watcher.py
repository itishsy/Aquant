import efinance as ef
from datetime import datetime
from signals.signals import deviates
import time


def watch_all():
    while True:
        now = datetime.now()
        try:
            if now.weekday() < 5 and now.hour in [10,11,13] and now.minute == 15:
                pass

        except Exception as e:
            print(e)
        finally:
            if now.minute == 1:
                print('[{}] daily task working'.format(now))
            time.sleep(60)
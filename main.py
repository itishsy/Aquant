import storage.database as db
from storage.fetcher import start_fetch
from strategy.macd_signal import signal

if __name__ == '__main__':
    db.init_schema()
    start_fetch(prefix='300223')
    signal('300223', klt=102)
    #signal('300223')

from engines import *
from datetime import datetime
from models.user import generate_pwd
from models.symbol import Symbol
from models.ticket import Ticket
from models.base import BaseModel, db
from candles.fetcher import fetch_all
from candles.storage import find_candles
from signals.divergence import diver_bottom
from candles.marker import mark


def test_search(eng_name):
    eng = engine.strategy[eng_name]()
    eng.strategy = eng_name
    print("[{}] {} start...".format(datetime.now(), eng_name))
    eng.do_search()
    print("[{}] {} end".format(datetime.now(), eng_name))


def test_watch(eng_name):
    eng = engine.strategy[eng_name]()
    eng.strategy = eng_name
    print("[{}] {} start...".format(datetime.now(), eng_name))
    eng.start_watch()
    print("[{}] {} end".format(datetime.now(), eng_name))


def test_model():
    # generate_pwd('')
    # print('done!')
    db.connect()
    db.create_tables([Ticket])


def monthly_diver_bottom():
    # fetch_all(freq=103)
    sbs = Symbol.actives()
    for sb in sbs:
        candles = find_candles(sb.code, freq=103)
        # candles = mark(candles)
        sis = diver_bottom(candles)
        if len(sis) > 0 and sis[-1].dt > '2024-01-01' and candles[-1].close < 15:
            if sb.code.startswith('60'):
                print("http://xueqiu.com/S/SH{} {}".format(sb.code,sis[-1].dt))
            else:
                print("http://xueqiu.com/S/SZ{} {}".format(sb.code,sis[-1].dt))


if __name__ == '__main__':
    # Symbol.fetch()
    # test_watch('p60')
    # test_search('u20')
    # test_model()
    monthly_diver_bottom()

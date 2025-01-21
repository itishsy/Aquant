from engines import *
from datetime import datetime
from models.symbol import Symbol
from models.symbol import Symbol
from models.engine import Engine
from models.ticket import Ticket
from models.base import BaseModel, db
from candles.storage import find_candles
from candles.finance import fetch_and_save
from signals.divergence import diver_bottom
from candles.marker import mark
from strategies.ma20 import MA20


def search_choice(engines):
    for eng_name in engines:
        eng = engine.strategy[eng_name]()
        eng.strategy = eng_name
        print("[{}] {} start...".format(datetime.now(), eng_name))
        eng.do_search()
        print("[{}] {} end".format(datetime.now(), eng_name))


def test_engine(eng_name):
    # eng.strategy = eng_name
    print("[{}] {} start...".format(datetime.now(), eng_name))
    engine.engines[eng_name]().start()
    print("[{}] {} end".format(datetime.now(), eng_name))


def find_month_divergence():
    symbols = Symbol.select()
    for sym in symbols:
        try:
            candles = find_candles(sym.code, freq=103)
            sis = diver_bottom(candles)
            print('search single code=', sym.code, 'result:', len(sis))
            if len(sis) > 0:
                for si in sis:
                    si.save()
        except Exception as e:
            print(e)


def test_model():
    # generate_pwd('')
    # print('done!')
    db.connect()
    db.create_tables([Ticket])


def monthly_diver_bottom():
    # fetch_all(freq=103)
    sbs = Symbol.actives()
    for sb in sbs:
        try:
            fetch_and_save(sb.code, freq=103)
            candles = find_candles(sb.code, freq=103)
            sis = diver_bottom(candles)
            # print('find monthly diver bottom: {}, results:{}'.format(sb.code, len(sis)))
            if len(sis) > 0 and sis[-1].dt > '2024-01-01':
                if sb.code.startswith('60'):
                    print("http://xueqiu.com/S/SH{} {}".format(sb.code, sis[-1].dt))
                else:
                    print("http://xueqiu.com/S/SZ{} {}".format(sb.code, sis[-1].dt))
        except Exception as e:
            print(e)


def engine_job():
    now = datetime.now()
    n_val = now.hour * 100 + now.minute
    ens = Engine.select().where(Engine.status == 0)
    for eng in ens:
        if eng.job_from < n_val < eng.job_to:
            if eng.job_times == 1 and eng.run_end > datetime.strptime(datetime.now().strftime("%Y-%m-%d 00:00:01"),
                                                                      "%Y-%m-%d %H:%M:%S"):
                continue
            try:
                eng.status = 1
                eng.run_start = datetime.now()
                eng.save()
                if engine.engines.get(eng.method) is None:
                    eval(eng.name + '.' + eng.method + '()')
                else:
                    engine.engines[eng.method]().start()
                eng.status = 0
                eng.run_end = datetime.now()
                eng.save()
            except Exception as e:
                eng.status = 0
                eng.save()
                print(e)


if __name__ == '__main__':
    # test_engine('u305')
    # test_engine('u615')
    test_engine('reviewNotify')
    # test_model()
    # monthly_diver_bottom()
    # engine_job()
    # ma20 = MA20()
    # ma20.search('002587')

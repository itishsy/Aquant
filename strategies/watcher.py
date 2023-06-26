from datetime import datetime, timedelta
from signals.divergence import diver_top, diver_bottom
from storage.fetcher import fetch_and_save
from storage.dba import find_candles
from models.ticket import Ticket
from models.trade import Trade
from models.signal import Signal
from models.component import Component
from common.dicts import freq_level
from common.utils import dt_format
import traceback
import time


def freq_collect(ti: Ticket):
    fqs = []
    bfs = freq_level(ti.buy)
    sfs = freq_level(ti.sell)
    for bf in bfs:
        if not fqs.__contains__(bf):
            fqs.append(bf)
    for sf in sfs:
        if not fqs.__contains__(sf):
            fqs.append(sf)
    return fqs


def is_watch_time(freq):
    now = datetime.now()
    hm = now.hour * 100 + now.minute
    if now.weekday() < 5:
        if freq == 5 and hm in [946, 1006, 1016, 1036, 1056,
                                1106, 1116, 1136, 1316, 1331, 1346,
                                1406, 1421, 1436, 1451]:
            return True
        if freq == 15 and hm in [1001, 1031, 1101, 1131,
                                 1331, 1401, 1431, 1501]:
            return True
        if freq in [30, 60] and hm in [1031, 1131, 1401, 1451]:
            return True
        if freq == 120 and hm in [1125, 1450, 1510]:
            return True
        if freq == 201 and hm in [1450, 1510]:
            return True
    return False


def is_trade_time():
    now = datetime.now()
    if now.weekday() > 4:
        return False

    return 930 < now_hm() < 1530


def now_hm():
    now = datetime.now()
    hm = now.hour * 100 + now.minute
    return hm


def deal(ti: Ticket):
    fqs = freq_level(ti.watch)
    for fq in fqs:
        if fq > 100 and now_hm() < 1430:
            continue

        fetch_and_save(ti.code, fq)
        cds = find_candles(ti.code, fq)
        if len(cds) < 50:
            return
        ldt = dt_format(cds[-1].dt)
        dbs = diver_bottom(cds)
        if len(dbs) > 0:  # and sis[-1].dt >= ldt:
            si = dbs[-1]
            print('buy code:{} freq:{},size:{}'.format(ti.code, fq, len(dbs)))
            if not Signal.select().where(Signal.code == ti.code, Signal.dt >= si.dt).exists():
                Signal.create(code=ti.code, name=ti.name, freq=fq, dt=si.dt, type=0, status=1, price=si.value,
                              created=datetime.now())
        dts = diver_top(cds)
        if len(dts) > 0:  # and sis[-1].dt >= ldt:
            si = dts[-1]
            print('sell code:{} freq:{},size:{}'.format(ti.code, fq, len(dts)))
            if not Signal.select().where(Signal.code == ti.code, Signal.dt >= si.dt).exists():
                Signal.create(code=ti.code, name=ti.name, freq=fq, dt=si.dt, type=1, status=1, price=si.value,
                              created=datetime.now())


def watch_all():
    tickets = []
    try:
        Component.update(status=2, run_start=datetime.now()).where(Component.name == 'watcher').execute()
        tis = Ticket.select().where(Ticket.status < 3)
        print('[{}] watch deal size:{}'.format(datetime.now(), len(tis)))
        for ti in tis:
            deal(ti)
        Component.update(status=1, run_end=datetime.now()).where(Component.name == 'watcher').execute()
    except Exception as e:
        traceback.print_exc()
    finally:
        return tickets


def daily_watch():
    print('[{}] watcher start'.format(datetime.now()))
    while True:
        now = datetime.now()
        try:
            Component.update(status=1, clock_time=now).where(Component.name == 'watcher').execute()
            if is_trade_time():
                watch_all()
        except Exception as e:
            print(e)
        finally:
            time.sleep(60 * 15)


if __name__ == '__main__':
    # watch_all()
    daily_watch()

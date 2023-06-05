from datetime import datetime, timedelta
from signals.divergence import diver_top, diver_bottom
from storage.fetcher import fetch_and_save
from storage.dba import find_candles
from models.ticket import Ticket
from models.trade import Trade
from common.utils import dt_format, freq_level
import traceback
import time

flag = False


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
    if now.weekday() < 5:
        return False
    else:
        hm = now.hour * 100 + now.minute
        return 930 < hm < 1530


def deal(ti: Ticket):
    fqs = freq_collect(ti)
    for fq in fqs:
        if flag or is_watch_time(fq):
            fetch_and_save(ti.code, fq)
            bfs = freq_level(ti.buy)
            sfs = freq_level(ti.sell)
            cds = find_candles(ti.code, fq)
            if len(cds) < 50:
                return
            ldt = dt_format(cds[-1].dt)
            if bfs.__contains__(fq):
                sis = diver_bottom(cds)
                if len(sis) > 0:  # and sis[-1].dt >= ldt:
                    si = sis[-1]
                    print('deal code:{} buy:{},size:{}'.format(ti.code, fq, len(sis)))
                    if not Trade.select().where(Trade.code == si.code, Trade.dt == si.dt, Trade.freq == fq,
                                                Trade.type == 0).exists():
                        Trade.create(code=ti.code, name=ti.name, freq=fq, dt=si.dt, type=0, price=si.value, created=datetime.now())
            if sfs.__contains__(fq):
                sis = diver_top(cds)
                if len(sis) > 0:  # and sis[-1].dt >= ldt:
                    si = sis[-1]
                    print('deal code:{} sell:{},size:{}'.format(ti.code, fq, len(sis)))
                    if not Trade.select().where(Trade.code == si.code, Trade.dt == si.dt, Trade.freq == fq,
                                                Trade.type == 1).exists():
                        Trade.create(code=ti.code, name=ti.name, freq=fq, dt=si.dt, type=1, price=si.value, created=datetime.now())


def watch_all():
    tickets = []
    try:
        tis = Ticket.select().where(Ticket.status < 2)
        for ti in tis:
            deal(ti)
    except Exception as e:
        traceback.print_exc()
    finally:
        return tickets


def daily_watch():
    print('[{}] watcher working ...'.format(datetime.now()))
    while True:
        now = datetime.now()
        try:
            if is_trade_time():
                watch_all()
        except Exception as e:
            print(e)
        finally:
            if now.minute == 1:
                print('[{}] watcher working ...'.format(now))
            time.sleep(30)


if __name__ == '__main__':
    flag = True
    watch_all()
    #daily_watch()

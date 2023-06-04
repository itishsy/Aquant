from datetime import datetime, timedelta
from signals.divergence import diver_top, diver_bottom
from storage.fetcher import fetch_and_save
from storage.dba import find_candles
from models.ticket import Ticket
from models.trade import Trade
from common.utils import dt_format, is_deal_time
import traceback
import time

flag = False

def freq_collect(ti: Ticket):
    fqs = []
    bfs = ti.buy.split(',')
    sfs = ti.sell.split(',')
    for bf in bfs:
        if not fqs.__contains__(bf):
            fqs.append(bf)
    for sf in sfs:
        if not fqs.__contains__(sf):
            fqs.append(sf)
    return fqs


def deal(ti: Ticket):
    fqs = freq_collect(ti)
    for fq in fqs:
        if flag or is_deal_time(fq):
            fetch_and_save(ti.code, fq)
            bfs = ti.buy.split(',')
            sfs = ti.sell.split(',')
            cds = find_candles(ti.code, fq)
            if len(cds) < 50:
                return
            ldt = dt_format(cds[-1].dt)
            if bfs.__contains__(fq):
                sis = diver_bottom(cds)
                print('deal code:{} buy:{},size:{}'.format(ti.code,fq,len(sis)))
                if len(sis) > 0: # and sis[-1].dt >= ldt:
                    Trade.create(code=ti.code, name=ti.name, freq=fq, dt=sis[-1].dt, type=0, price=sis[-1].value)
            if sfs.__contains__(fq):
                sis = diver_top(cds)
                print('deal code:{} sell:{},size:{}'.format(ti.code,fq,len(sis)))
                if len(sis) > 0: # and sis[-1].dt >= ldt:
                    Trade.create(code=ti.code, name=ti.name, freq=fq, dt=sis[-1].dt, type=1, price=sis[-1].value)


def watch_all():
    tickets = []
    try:
        tis = Ticket.select().where(Ticket.status < 2)
        for ti in tis:
            deal(ti)
    except Exception as e:
        print(e)
    finally:
        return tickets


def daily_watch():
    print('[{}] watcher working ...'.format(datetime.now()))
    while True:
        now = datetime.now()
        try:
            if now.weekday() < 5:
                watch_all()
        except Exception as e:
            print(e)
        finally:
            if now.minute == 1:
                print('[{}] searcher working ...'.format(now))
            time.sleep(60)


if __name__ == '__main__':
    flag = True
    watch_all()

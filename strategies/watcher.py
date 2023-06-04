from datetime import datetime, timedelta
from signals.divergence import diver_top, diver_bottom
from storage.fetcher import fetch_and_save
from storage.dba import find_candles
from models.ticket import Ticket
from models.trade import Trade
from common.utils import dt_format, is_deal_time
import traceback

flag = False

def storage_data(ti: Ticket):
    fqs = []
    bfs = ti.buy.split(',')
    sfs = ti.sell.split(',')
    for bf in bfs:
        if not fqs.__contains__(bf):
            fqs.append(bf)
    for sf in sfs:
        if not fqs.__contains__(sf):
            fqs.append(sf)
    for fq in fqs:
        if flag or is_deal_time(fq):
            fetch_and_save(ti.code, fq)


def deal_buy(ti: Ticket):
    bfs = ti.buy.split(',')
    for fq in bfs:
        if flag or is_deal_time(fq):
            cds = find_candles(ti.code, fq)
            if len(cds) < 50:
                return
            ldt = dt_format(cds[-1].dt)
            sis = diver_bottom(cds)
            if len(sis) > 0 and sis[-1].dt >= ldt:
                Trade.create(code=ti.code, name=ti.name, freq=fq, dt=sis[-1].dt, type=0, price=sis[-1].value)


def deal_sell(ti: Ticket):
    sfs = ti.sell.split(',')
    for fq in sfs:
        if flag or is_deal_time(fq):
            cds = find_candles(ti.code, fq)
            if len(cds) < 50:
                return
            ldt = dt_format(cds[-1].dt)
            # TODO cut and change status
            sis = diver_top(cds)
            if len(sis) > 0 and sis[-1].dt >= ldt:
                Trade.create(code=ti.code, name=ti.name, freq=fq, dt=sis[-1].dt, type=1, price=sis[-1].value)


def trade_watch():
    tickets = []
    try:
        tis = Ticket.select().where(Ticket.status < 2)
        for ti in tis:
            storage_data(ti)
            deal_buy(ti)
            deal_sell(ti)
    except Exception as e:
        print(e)
    finally:
        return tickets


if __name__ == '__main__':
    pass

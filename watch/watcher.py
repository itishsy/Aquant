import time
from datetime import datetime, timedelta
from signals.signals import divergence
from storage.db import find_tickets, update_ticket
from storage.fetcher import fetch_data
from storage.marker import mark
from typing import List
from entities.ticket import Ticket
import qywx
import traceback


def get_tickets() -> List[Ticket]:
    tickets = []
    try:
        now = datetime.now()
        if True or now.weekday() < 5 and now.hour in [10, 11, 13, 14] and now.minute in [5, 25, 45]:
            fts = find_tickets()
            for t in fts:
                if t.freq in [5, 15]:
                    s = 10 if t.freq == 15 else 5
                    candles = fetch_data(t.code, t.freq, (datetime.now() - timedelta(s)).strftime('%Y%m%d'))
                    candles = mark(candles)
                    if len(candles) > 0:
                        des = divergence(candles, t.type == 1)
                        if len(des) > 0 and des[-1].dt >= datetime.now().strftime('%Y-%m-%d'):
                            t.dt = des[-1].dt
                            t.updated = datetime.now()
                            tickets.append(t)
    except Exception as e:
        print(e)
    finally:
        return tickets


if __name__ == '__main__':
    while True:
        try:
            content = ''
            mappings = []
            tis = get_tickets()
            for ti in tis:
                content = 'code={},freq={},dt={};{}'.format(ti.code, ti.freq, ti.dt, content)
                dic = {'id': ti.id, 'dt': ti.dt, 'status': 2, 'updated': ti.updated}
                mappings.append(dic)
            res = qywx.send_msg(content)
            if res and len(mappings) > 0:
                update_ticket(mappings)
        except Exception:
            traceback.print_exc()
        finally:
            if datetime.now().minute == 0:
                print('[{}] watching'.format(datetime.now()))
            time.sleep(60)

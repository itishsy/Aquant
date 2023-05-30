import time
from datetime import datetime, timedelta
from signals.divergence import diver_top, diver_bottom
from models.trade import update_trade
from storage.fetcher import fetch_data
from storage.marker import mark
from typing import List
from models.ticket import find_tickets
import qywx
import traceback


def daily_watch():
    tickets = []
    try:
        now = datetime.now()
        if now.weekday() < 5 and now.hour in [10, 11, 13, 14] and now.minute in [5, 25, 45]:
            tis = find_tickets()
            for ti in tis:
                if ti.b_freq in [5, 15]:
                    s = 10 if t.freq == 15 else 5
                    candles = fetch_data(t.code, t.freq, (datetime.now() - timedelta(s)).strftime('%Y%m%d'))
                    candles = mark(candles)
                    if len(candles) > 0:
                        if t.type == 1:
                            des = diver_top(candles)
                        else:
                            des = diver_bottom(candles)
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
            tis = find_tickets()
            for ti in tis:
                content = 'code={},freq={},dt={};{}'.format(ti.code, ti.freq, ti.dt, content)
                dic = {'id': ti.id, 'dt': ti.dt, 'status': 2, 'updated': ti.updated}
                mappings.append(dic)
            res = qywx.send_msg(content)
            if res and len(mappings) > 0:
                update_trade(mappings)
        except Exception:
            traceback.print_exc()
        finally:
            if datetime.now().minute == 0:
                print('[{}] watching'.format(datetime.now()))
            time.sleep(60)

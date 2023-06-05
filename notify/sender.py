from models.trade import Trade
from datetime import datetime
from notify.qywx import send_msg
import time
import traceback


def find_notify_content():
    trs = Trade.select().where(Trade.notify == 0).order_by(Trade.id).limit(5)
    content = ''
    for tr in trs:
        content = 'code={},freq={},dt={};{}'.format(tr.code, tr.freq, tr.dt, content)
    return content


def update_notify_status():
    trs = Trade.select().where(Trade.notify == 0).order_by(Trade.id).limit(5)
    for tr in trs:
        tr.notify = 1
    Trade.bulk_update(trs, fields=['notify'], batch_size=50)


if __name__ == '__main__':
    while True:
        try:
            message = find_notify_content()
            if send_msg(message):
                update_notify_status()
            if datetime.now().minute == 0:
                print('[{}] sender working'.format(datetime.now()))
        except Exception:
            traceback.print_exc()
        finally:
            time.sleep(60)

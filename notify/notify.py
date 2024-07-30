from models.signal import Signal
from datetime import datetime
from notify.qywx import Qywx
from notify.mail import send


qywx = Qywx()


def find_notify_content():
    sis = Signal.select().where(Signal.notify == 0).order_by(Signal.id).limit(5)
    content = ''
    for si in sis:
        # link = 'http://xueqiu.com/S/{}{}'.format('SH' if si.code.startswith('60') else 'SZ', si.code)
        content = '{}-{}-{}-{}\n{}'.format(si.stage, si.freq, si.code,
                                           str(si.dt).replace('-', '').replace(' ', '').replace(':', ''), content)
    return content


def update_notify_status():
    sis = Signal.select().where(Signal.notify == 0).order_by(Signal.id).limit(5)
    for si in sis:
        si.notify = 1
        si.updated = datetime.now()
        si.save()


def do_notify():
    content = find_notify_content()
    if len(content) > 0:
        send(content)
        qywx.send(content)


def start_notify():
    qywx.send('start')
    send('start')





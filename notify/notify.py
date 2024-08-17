from models.signal import Signal
from datetime import datetime
from notify.qywx import Qywx
from notify.mail import send_email


class Notify:

    def __init__(self):
        self.content = None
        self.qywx = Qywx()
        self.qywx.send('start')
        send_email('start')

    def do_send(self):
        self.find_notify_content()
        if self.content is not None:
            print("send content:", self.content, "!")
            # self.qywx.send(self.content)
            if send_email(self.content):
                self.update_notify_status()

    def find_notify_content(self):
        sis = Signal.select().where(Signal.notify == 0).order_by(Signal.id).limit(5)
        if len(sis) == 0:
            self.content = None
        else:
            for si in sis:
                # link = 'http://xueqiu.com/S/{}{}'.format('SH' if si.code.startswith('60') else 'SZ', si.code)
                self.content = '{}-{}-{}-{}\n{}'.format(si.stage, si.freq, si.code,
                                                   str(si.dt).replace('-', '').replace(' ', '').replace(':', ''), self.content)

    def update_notify_status(self):
        self.content = None
        sis = Signal.select().where(Signal.notify == 0).order_by(Signal.id).limit(5)
        for si in sis:
            si.notify = 1
            si.updated = datetime.now()
            si.save()

#
# def do_notify():
#     content = find_notify_content()
#     if len(content) > 0:
#         send(content)
#         qywx.send(content)
#
#
# def start_notify():
#     qywx.send('start')
#     send('start')





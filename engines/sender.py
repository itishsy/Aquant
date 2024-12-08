import datetime

from engines.engine import Sender, job_engine
from models.signal import Signal
import smtplib
import traceback


@job_engine
class email(Sender):

    def send(self):
        sis = Signal.select().where(Signal.notify == 0)
        msg = ''
        for si in sis:
            if si.code.startswith('60'):
                msg = msg + "http://xueqiu.com/S/SH{} {} ".format(si.code, si.dt)
            else:
                msg = msg + "http://xueqiu.com/S/SZ{} {} ".format(si.code, si.dt)

        if msg != '':
            try:
                smtp_server = "smtp.163.com"
                smtp_username = "itishsy@163.com"
                smtp_password = "KSEJTXDLZLXNBMMI"
                smtp = smtplib.SMTP(smtp_server, port=25)
                smtp.starttls()
                smtp.login(smtp_username, smtp_password)
                from_email = "itishsy@163.com"
                to_email = "279440948@qq.com"
                subject = "Signal"
                body = msg
                message = f"From: {from_email}\nTo: {to_email}\nSubject: {subject}\n\n{body}"
                smtp.sendmail(from_email, to_email, message)
                smtp.quit()
                for si in sis:
                    si.notify = 1
                    si.updated = datetime.datetime.now()
                    si.save()
            except Exception as e:
                traceback.print_exc()
            return False



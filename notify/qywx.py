import datetime

from components.sender import *
import logging
from models.signal import Signal


class Qywx(RPA):
    def send(self, content):
        try:
            self.access("https://work.weixin.qq.com/wework_admin/frame#index")
            if self.exists(By.ID, "menu_index", 60):
                if self.exists(By.LINK_TEXT, '离开此页', 5):
                    self.click(By.LINK_TEXT, '离开此页')
                self.access("https://work.weixin.qq.com/wework_admin/frame#/message/5629503566587437")
                if self.exists(By.LINK_TEXT, '发送', 20):
                    self.click(By.LINK_TEXT, '选择发送范围')
                    self.click(By.LINK_TEXT, '全选')
                    self.click(By.LINK_TEXT, '确认')
                    self.input(By.TAG_NAME, 'textarea', content)
                    self.click(By.LINK_TEXT, '发送')
                    self.click(By.LINK_TEXT, '确定')
                    return True
            else:
                print('maybe no login')
        except Exception as e:
            traceback.print_exc()
            logging.error('send wechat message failed')
        return False

    def find_signal_and_send(self):
        sis = Signal.select().where(Signal.notify == 0).order_by(Signal.id).limit(5)
        content = ''
        for si in sis:
            # link = 'http://xueqiu.com/S/{}{}'.format('SH' if si.code.startswith('60') else 'SZ', si.code)
            content = '{}-{}-{}-{}\n{}'.format(si.stage, si.freq, si.code, str(si.dt).replace('-', '').replace(' ', '').replace(':', ''), content)
        if content != '':
            if self.send(content):
                for si in sis:
                    si.notify = 1
                    si.updated = datetime.datetime.now()
                    si.save()


if __name__ == '__main__':
    qywx = Qywx()
    qywx.send("hello")

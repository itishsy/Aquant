from components.sender import *
import logging


class Qywx(RPA):
    def send(self, content):
        try:
            self.access("https://work.weixin.qq.com/wework_admin/frame#index")
            if self.exists(By.ID, "menu_index", 30):
                if self.exists(By.LINK_TEXT, '离开此页', 5):
                    self.click(By.LINK_TEXT, '离开此页')
                self.access("https://work.weixin.qq.com/wework_admin/frame#/message/5629503566587437")
                if self.exists(By.LINK_TEXT, '发消息', 10):
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


if __name__ == '__main__':
    qywx = Qywx()
    qywx.send("hello")

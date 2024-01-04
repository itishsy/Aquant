from components.rpa import *
import logging


def send_qywx(content):
    try:
        access("https://work.weixin.qq.com/wework_admin/frame#index")
        if exists(By.ID, "menu_index", 30):
            if exists(By.LINK_TEXT, '离开此页', 5):
                click(By.LINK_TEXT, '离开此页')
            access("https://work.weixin.qq.com/wework_admin/frame#/message/5629503566587437")
            if exists(By.LINK_TEXT, '发消息', 10):
                click(By.LINK_TEXT, '选择发送范围')
                click(By.LINK_TEXT, '全选')
                click(By.LINK_TEXT, '确认')
                input(By.TAG_NAME, 'textarea', content)
                click(By.LINK_TEXT, '发送')
                click(By.LINK_TEXT, '确定')
                return True
        else:
            print('maybe no login')
    except Exception as e:
        traceback.print_exc()
        logging.error('send wechat message failed')
    return False


if __name__ == '__main__':
    send_qywx("hello")

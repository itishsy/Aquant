import time
import traceback
from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions
from selenium.webdriver.common.by import By
import logging

options = webdriver.ChromeOptions()
driver = webdriver.Chrome(options=options)
driver.get("https://work.weixin.qq.com/wework_admin/frame#index")


def send_msg(content):
    try:
        driver.get("https://work.weixin.qq.com/wework_admin/frame#index")
        try:
            btn_lk = WebDriverWait(driver, 10).until(
                expected_conditions.presence_of_element_located((By.LINK_TEXT, '离开此页')))
            if btn_lk is not None:
                driver.execute_script('arguments[0].click();', btn_lk)
        except:
            pass
        driver.get("https://work.weixin.qq.com/wework_admin/frame#/message/5629503566587437")
        msg_panel = WebDriverWait(driver, 600).until(
            expected_conditions.presence_of_element_located((By.LINK_TEXT, '发消息')))
        if msg_panel is not None:
            if content == '':
                return

            print(content)
            element_click(By.LINK_TEXT, '选择发送范围')
            element_click(By.LINK_TEXT, '全选')
            element_click(By.LINK_TEXT, '确认')
            element_input(By.TAG_NAME, 'textarea', content)
            element_click(By.LINK_TEXT, '发送')
            element_click(By.LINK_TEXT, '确定')
            return True
        else:
            print('maybe no login')
            return False
    except Exception as e:
        traceback.print_exc()
        logging.error('send wechat message failed')
        return False


def element_click(by, name):
    el = WebDriverWait(driver, 20).until(
        expected_conditions.presence_of_element_located((by, name)))
    print('{}.click'.format(name))
    el.click()
    time.sleep(5)


def element_input(by, name, val):
    el = WebDriverWait(driver, 20).until(
        expected_conditions.presence_of_element_located((by, name)))
    print('{}.send_keys: {}'.format(name, val))
    el.send_keys(val)
    time.sleep(5)

import time
import traceback
from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions
from selenium.webdriver.common.by import By
import logging
from storage.db import find_signals, update_signal_notify
from typing import List
from entities.signal import Signal


def get_message(sgs: List[Signal]):
    msg1 = '123'
    signals = find_signals()
    # if len(signals) > 0:
    #     for s in sgs:
    #         msg1 = '【{}】, klt: {}, type: {}, datetime: {}; {}' \
    #             .format(s.code, s.klt, s.type, s.dt, msg1)
    return msg1


options = webdriver.ChromeOptions()
driver = webdriver.Chrome(options=options)
while True:
    try:
        driver.get("https://work.weixin.qq.com/wework_admin/frame#/message/5629503566587437")
        msg_panel = WebDriverWait(driver, 600).until(
            expected_conditions.presence_of_element_located((By.LINK_TEXT, '发消息')))
        if msg_panel is not None:
            msg = get_message()
            if msg == '':
                continue

            print(msg)
            btn_who = WebDriverWait(driver, 20).until(
                expected_conditions.presence_of_element_located((By.LINK_TEXT, '选择发送范围')))
            print('btn_who')
            btn_who.click()
            time.sleep(5)
            btn_all = WebDriverWait(driver, 20).until(
                expected_conditions.presence_of_element_located((By.LINK_TEXT, '全选')))
            btn_all.click()
            print('btn_all.click')
            time.sleep(5)
            btn_qr = WebDriverWait(driver, 20).until(
                expected_conditions.presence_of_element_located((By.LINK_TEXT, '确认')))
            btn_qr.click()
            print('btn_qr.click')
            time.sleep(5)
            txt_msg = WebDriverWait(driver, 20).until(
                expected_conditions.presence_of_element_located((By.TAG_NAME, 'textarea')))
            txt_msg.send_keys(msg)
            print('txt_msg.send_keys')
            time.sleep(5)
            btn_sender = WebDriverWait(driver, 20).until(
                expected_conditions.presence_of_element_located((By.LINK_TEXT, '发送')))
            driver.execute_script('arguments[0].click();', btn_sender)
            print('btn_sender.click')
            time.sleep(5)
            btn_ok = WebDriverWait(driver, 20).until(
                expected_conditions.presence_of_element_located((By.LINK_TEXT, '确定')))
            btn_ok.click()
            print('btn_ok.click')
            time.sleep(5)
        else:
            print('maybe no login')
    except Exception as e:
        traceback.print_exc()
        logging.error('send wechat message failed')
    finally:
        time.sleep(30)
        driver.get("https://work.weixin.qq.com/wework_admin/frame#index")
        print('msg time sleep 60')
        try:
            btn_lk = WebDriverWait(driver, 20).until(
                expected_conditions.presence_of_element_located((By.LINK_TEXT, '离开此页')))
            if btn_lk is not None:
                driver.execute_script('arguments[0].click();', btn_lk)
        except:
            pass
        finally:
            time.sleep(30)

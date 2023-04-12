from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions
from selenium.webdriver.common.by import By
import time

options = webdriver.ChromeOptions()
driver = webdriver.Chrome()

try:
    driver.get("https://work.weixin.qq.com/wework_admin/frame#/message/5629503566587437/7220327147662968804")
    msg_panel = WebDriverWait(driver, 600).until(
        expected_conditions.presence_of_element_located((By.TAG_NAME, 'textarea')))
    msg_panel.send_keys('hello')
    time.sleep(10)
    sender = driver.find_element(by=By.LINK_TEXT, value='发送')
    sender.click()
    time.sleep(10)
    btn_ok = driver.find_element(by=By.LINK_TEXT, value='确定')
    btn_ok.click()
    time.sleep(600)
finally:
    pass



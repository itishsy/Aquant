import time
import traceback
from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions
from selenium.webdriver.common.by import By
import logging

options = webdriver.ChromeOptions()
driver = webdriver.Chrome(options=options)


def access(url):
    driver.get(url)
    time.sleep(3)


def click(by, name):
    try:
        el = WebDriverWait(driver, 20).until(expected_conditions.presence_of_element_located((by, name)))
        print('{}.click()'.format(name))
        if el is not None:
            driver.execute_script("arguments[0].click();", el)
            return 1
        return 0
    except Exception as e:
        traceback.print_exc()
        return 0
    finally:
        time.sleep(2)


def input(by, name, val):
    try:
        el = WebDriverWait(driver, 20).until(
            expected_conditions.presence_of_element_located((by, name)))
        if el is not None:
            print('{}.input: {}'.format(name, val))
            el.send_keys(val)
            return 1
        return 0
    except Exception as e:
        traceback.print_exc()
        return 0
    finally:
        time.sleep(2)


def exists(by, name, timeout):
    try:
        el = WebDriverWait(driver, timeout).until(
            expected_conditions.presence_of_element_located((by, name)))
        if el is not None:
            return True
        return False
    except Exception as e:
        return False
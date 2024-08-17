import time
import traceback
from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions
from selenium.webdriver.common.by import By
import logging


class RPA:
    def __init__(self, headless=False):
        print("=====start driver=====")
        options = webdriver.ChromeOptions()
        if headless:
            options.add_argument('--headless')
        self.driver = webdriver.Chrome(options=options)

    def access(self, url):
        self.driver.get(url)
        time.sleep(2)

    def click(self, by, name):
        try:
            el = WebDriverWait(self.driver, 20).until(expected_conditions.presence_of_element_located((by, name)))
            print('{}.click()'.format(name))
            if el is not None:
                self.driver.execute_script("arguments[0].click();", el)
                return 1
            return 0
        except Exception as e:
            traceback.print_exc()
            return 0
        finally:
            time.sleep(2)

    def input(self, by, name, val):
        try:
            el = WebDriverWait(self.driver, 20).until(
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

    def exists(self, by, name, timeout):
        try:
            el = WebDriverWait(self.driver, timeout).until(
                expected_conditions.presence_of_element_located((by, name)))
            if el is not None:
                return True
            return False
        except Exception as e:
            return False
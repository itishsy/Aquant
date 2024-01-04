from components.rpa import *
import logging

def find_hot():
    access("https://xueqiu.com/hq")
    el = WebDriverWait(driver, 10).until(expected_conditions.presence_of_element_located((By.CLASS_NAME, "style_hot-stock-list_3Ty")))
    ele = driver.find_element(By.CLASS_NAME, "style_hot-stock-list_3Ty")
    ele.find_elements()

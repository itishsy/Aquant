from components.rpa import *
import logging


def find_hot():
    access("https://xueqiu.com/hq")
    ele = driver.find_element(By.CLASS_NAME, "style_hot-stock-list_3Ty")
    els = ele.find_elements(By.TAG_NAME, "a")
    for el in els:
        href = el.get_attribute("href")
        code = href.split("/S/")[1]
        if code.startswith("SH"):
            print(code.replace("SH", ''))
        elif code.startswith("SZ"):
            print(code.replace("SZ", ''))


if __name__ == '__main__':
    find_hot()

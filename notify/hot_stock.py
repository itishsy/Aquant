from components.rpa import *
from models.hot import Hot
import json


class HotStock(RPA):

    def __init__(self):
        super().__init__(headless=True)

    def xueqiu(self):
        self.access("https://xueqiu.com/hq")
        self.access("https://stock.xueqiu.com/v5/stock/hot_stock/list.json?size=20&_type=12&type=22")
        txt = self.driver.find_element(By.TAG_NAME, "pre").text
        json_data = json.loads(txt)
        idx = 1
        for item in json_data['data']['items']:
            cod = item['code'][2:]
            Hot.add(cod, item['name'], "雪球", idx)
            print(idx, cod, item['name'])
            idx = idx + 1
            if idx > 20:
                return

    def taoguba(self):
        self.access("https://www.taoguba.com.cn/new/nrnt/getNoticeStock?type=D")
        txt = self.driver.find_element(By.TAG_NAME, "pre").text
        json_data = json.loads(txt)
        idx = 1
        for item in json_data['dto']:
            cod = item['fullCode'][2:]
            Hot.add(cod, item['stockName'], "淘股吧", idx)
            print(idx, cod, item['stockName'])
            idx = idx + 1
            if idx > 20:
                return

    def guba(self):
        self.access("https://guba.eastmoney.com/rank/")
        els = self.driver.find_elements(By.CLASS_NAME, "nametd_box")
        idx = 1
        for el in els:
            a = el.find_element(By.TAG_NAME, "a")
            cod = a.get_attribute("class").replace("stock_name_", "")
            Hot.add(cod, a.text, "东方财富", idx)
            print(cod, a.text)
            idx = idx + 1
            if idx > 20:
                return

    def fetch_all(self):
        self.xueqiu()
        self.taoguba()
        self.guba()


if __name__ == '__main__':
    hot = HotStock()
    hot.fetch_all()

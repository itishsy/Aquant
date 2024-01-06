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
            Hot.add(item['code'], item['name'], "雪球", idx)
            print(idx, item['code'], item['name'])
            idx = idx + 1
            if idx > 20:
                return

    def taoguba(self):
        self.access("https://www.taoguba.com.cn/new/nrnt/getNoticeStock?type=D")
        txt = self.driver.find_element(By.TAG_NAME, "pre").text
        json_data = json.loads(txt)
        idx = 1
        for item in json_data['dto']:
            Hot.add(item['fullCode'], item['stockName'], "淘股吧", idx)
            print(idx, item['fullCode'], item['stockName'])
            idx = idx + 1
            if idx > 20:
                return

    def fetch_all(self):
        self.xueqiu()
        self.taoguba()


if __name__ == '__main__':
    hot = HotStock()
    hot.fetch_all()

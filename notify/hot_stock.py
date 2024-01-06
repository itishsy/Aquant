from components.rpa import *
from models.hot import Hot
import json


def xueqiu_hot():
    access("https://xueqiu.com/hq")
    access("https://stock.xueqiu.com/v5/stock/hot_stock/list.json?size=20&_type=12&type=22")
    txt = driver.find_element(By.TAG_NAME, "pre").text
    json_data = json.loads(txt)
    idx = 1
    for item in json_data['data']['items']:
        Hot.add(item['code'], item['name'], "雪球", idx)
        print(idx, item['code'], item['name'])
        idx = idx + 1
        if idx > 20:
            return


def taoguba_hot():
    access("https://www.taoguba.com.cn/new/nrnt/getNoticeStock?type=D")
    txt = driver.find_element(By.TAG_NAME, "pre").text
    json_data = json.loads(txt)
    idx = 1
    for item in json_data['dto']:
        Hot.add(item['fullCode'], item['stockName'], "淘股吧", idx)
        print(idx, item['fullCode'], item['stockName'])
        idx = idx + 1
        if idx > 20:
            return


if __name__ == '__main__':
    xueqiu_hot()
    taoguba_hot()

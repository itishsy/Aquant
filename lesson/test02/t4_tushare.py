import tushare as ts
from dataclasses import dataclass
import numpy as np
from typing import List


@dataclass
class Tsc:

    def __init__(self, series=None):
        for key in series.keys():
            setattr(self, key, series[key])

    ts_code: str
    trade_date: str
    open: float
    high: float
    low: float
    close: float
    vol: float


# from t3_mysql import save_to_table
#
# # 获取两市股票信息
pro = ts.pro_api('92780d6f7fae57eb76e8d97229d7f91f67d0dd843db5088c6e595c28')
#
# # 拉取数据
df = pro.daily(**{
    "ts_code": "",
    "trade_date": "",
    "start_date": "",
    "end_date": "",
    "offset": "",
    "limit": ""
}, fields=[
    "ts_code",
    "trade_date",
    "open",
    "high",
    "low",
    "close",
    "vol"
])
# print(df)
# list = np.array(df).tolist()
tss = []
for i, row in df.iterrows():
    tss.append(Tsc(row))
print(tss[3])
print(tss[200].ts_code)


# save_to_table(df,'stock_basic')
#


# df = pro ts.get_hist_data('600848')
# print(df)

import tushare as ts
from t3_mysql import save_to_table

# 获取两市股票信息
pro = ts.pro_api('92780d6f7fae57eb76e8d97229d7f91f67d0dd843db5088c6e595c28')

# 拉取数据
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
    "pre_close",
    "change",
    "pct_chg",
    "vol",
    "amount"
])
print(df)
save_to_table(df,'stock_basic')
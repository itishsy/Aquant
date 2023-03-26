import pandas as pd
import numpy as np
import time
from datetime import datetime

data = np.random.randint(1,20,size=9).reshape(3,3)
df = pd.DataFrame(data,index=list('abc'),columns=list("ABC"))
print(df)

print("=================# 取出指定列数据, df['B']========================")
print(df['B'])
print("=================# 取出指定行数据, df.loc['b']========================")
print(df.loc['b'])

from t1_numpy import data_gen


def data_k_gen():
    columns = ['Date','Open','High','Low','Close']

    # 日期
    date = pd.date_range(start='20230301',end='20230401',freq='D')
    size=len(date)
    open = data_gen(size=size,low=23,high=28)
    high = data_gen(size=size,low=28,high=30)
    low = data_gen(size=size,low=20,high=23)
    close = data_gen(size=size,low=23,high=28)

    df_k = pd.DataFrame(columns=columns)
    df_k['Date'] = date
    df_k['Open'] = open
    df_k['High'] = high
    df_k['Low'] = low
    df_k['Close'] = close

    #print("行情数据：\n",df_k)

    row = {
        'Date': datetime.strptime('2023-04-02','%Y-%m-%d'),
        'Open': 24.91,
        'High': 29.98,
        'Low': 22.73,
        'Close': 25.58
    }
    #df_k = pd.concat([df_k,row])
    df_k = df_k.append(row,ignore_index=True)
    df_k = df_k.set_index('Date',drop=True)
    #print(df_k.loc['2023-03-21'])
    return df_k

def draw_k_line(df_data):
    data_k_list = []
    date_array = []
    for d,r in df_data.iterrows():
        t = date2num(d)
        date_array.append(t)
        open,high,low,close = r
        row = (t, open, high, low, close)
        data_k_list.append(row)

def date2num(date_time):
    year = '%d' % date_time.year
    month = date_time.month
    str_month = '%d' % month;
    if month < 10:
        str_month = '0%d' % month
    day = date_time.day
    str_day = '%d' % day
    if day < 10:
        str_day = '0%d' % day
    return int(year+str_month+str_day)


data = data_k_gen()
draw_k_line(data)

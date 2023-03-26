import talib
from storage import read
import numpy as np
import pandas as pd


stock_code= '300059'

#data = read(stock_code, field="日期 as trade_date, 开盘 as open, 最高 as high, 最低 as low, 收盘 as close, 成交量 as vol")
data = read(stock_code, field="收盘", limit=100)
# 指定列
close=data['收盘'].values
"""data.index = data['trade_date']
data.drop(columns=['trade_date'], inplace=True)
data.columns = ['open', 'high', 'low', 'close', 'volume']
data.sort_index(inplace=True)"""

wma=talib.WMA(close,timeperiod=15)
dema = talib.DEMA(close, timeperiod=15)

b_list = dema - wma
#print(b_list)
# 标注快速大于慢速的点
signal_tip = np.where(b_list > 0, 1, 0)
#print(signal_tip)
# 标注慢速大于快速的点
signal_tip = np.where(b_list < 0, -1, signal_tip)
#print(signal_tip)
# 标记
print(data.index)
df = pd.DataFrame(signal_tip, index=data.index)
print(df)
signal = np.sign(df - df.shift(1))

#print(signal)
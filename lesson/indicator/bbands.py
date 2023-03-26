from storage import read
import mplfinance as mpf
import talib as ta
import numpy as np
import pandas as pd


stock_code= '300059'
#
data = read(stock_code,
            field="CAST(日期 AS DATETIME) as trade_date,开盘 as open, 最高 as high, 最低 as low, 收盘 as close, 成交量 as volume",
            limit=500)

data.set_index('trade_date',drop=True,inplace=True)
data.sort_index(inplace=True)

upperband, middleband, lowerband = ta.BBANDS(data.close, timeperiod = 20, nbdevup=2.0, nbdevdn=2.0, matype=0)

# 画图-可视化
add_plot = [
    # 上轨
    mpf.make_addplot(upperband, color='y'),
    # 中轨
    mpf.make_addplot(middleband, color='w'),
    # 下轨
    mpf.make_addplot(lowerband, color='m')
]
# 指定图形属性
my_color = mpf.make_marketcolors(up='red', down='cyan', volume='blue', inherit=True)
my_style = mpf.make_mpf_style(
    facecolor = 'black',
    marketcolors=my_color,
    gridaxis='horizontal',
    gridcolor='red',
    gridstyle='--',
    y_on_right=False
)
mpf.plot(data,
         addplot=add_plot,
         type='candle',
         style = my_style,
         figratio=(1920, 1080),
         figscale=1,
         volume=True,
         savefig='bbands_{}.png'.format(stock_code)
         )
#mpf.show()


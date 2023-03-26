from storage import read,insert
from datetime import datetime
#import mplfinance as mpf
import talib as ta
import numpy as np
import pandas as pd


def select_last6(stock_code):
    start = datetime(2022, 1, 1)
    k_data = read(stock_code, beg=start, field='open,high,low,close,volume,datetime')

    k_data.set_index('datetime',drop=True,inplace=True)
    k_data.sort_index(inplace=True)

    diff,dea,macd = ta.MACD(k_data.close, fastperiod=12, slowperiod=26, signalperiod=9)

    k_data['diff']=diff
    k_data['dea']=dea
    k_data['macd']=macd*2
    k_data['inflection']=0


    i=0
    l=len(k_data)
    #k_inflection = k_data
    for i in range(l):
        if i>0 and i<(l-1):
            i_macd_0 = k_data.iloc[i-1]['macd']
            i_macd = k_data.iloc[i]['macd']
            i_macd_2 = k_data.iloc[i+1]['macd']
            if i_macd_0 < 0 and i_macd > 0:
                k_data.iloc[i-1,k_data.columns.get_loc('inflection')] = -1
                k_data.iloc[i,k_data.columns.get_loc('inflection')] = 1
            if i_macd_0 > 0 and i_macd < 0:
                k_data.iloc[i-1,k_data.columns.get_loc('inflection')] = 1
                k_data.iloc[i,k_data.columns.get_loc('inflection')] = -1

            if abs(i_macd_0) < abs(i_macd) and abs(i_macd_2) < abs(i_macd):
                if i_macd < 0:
                    k_data.iloc[i-1,k_data.columns.get_loc('inflection')] = -2
                    k_data.iloc[i,k_data.columns.get_loc('inflection')] = -3
                    k_data.iloc[i+1,k_data.columns.get_loc('inflection')] = -2
                else:
                    k_data.iloc[i-1,k_data.columns.get_loc('inflection')] = 2
                    k_data.iloc[i,k_data.columns.get_loc('inflection')] = 3
                    k_data.iloc[i+1,k_data.columns.get_loc('inflection')] = 2

    k_inflection = k_data[k_data['inflection'] != 0]
    k_inflection = k_inflection[['close','diff','dea','macd','inflection']]
    last6 = k_inflection.tail(6)
    last6.sort_index(axis=0,ascending=False,inplace=True)
    return last6

def is_bc_stage(last6):
    last6_3 = last6[last6['inflection'] == -3]
    if len(last6_3) != 2:
        return False
    lst = last6_3.iloc[0]
    pre = last6_3.iloc[1]

    if lst.close > pre.close and lst.diff > pre.diff:
        return False


"""
#macdhist值处理
origin_macd_up = macdhist*2;
origin_macd_up[origin_macd_up<0]=0
macd_pos= origin_macd_up

origin_macd_dn= macdhist*2;
origin_macd_dn[origin_macd_dn>0]=0
macd_neg= origin_macd_dn
"""


# 画图-可视化

"""
add_plot = [
    # DIFF
    mpf.make_addplot(diff, panel=2, color='fuchsia', secondary_y=True),
    # DEA
    mpf.make_addplot(dea, panel=2, color='w', secondary_y=True),
    # MACDHIST#mpf.make_addplot(MACDHIST, type='bar', panel=2, color='cyan', secondary_y=True)
    mpf.make_addplot(macd_pos, type='bar', panel=2, color='r', secondary_y=True),
    mpf.make_addplot(macd_neg, type='bar', panel=2, color='cyan', secondary_y=True)
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
         figscale=1.88,
         volume=True,
         main_panel=0,
         volume_panel=1,
         savefig='macd_{}.png'.format(stock_code)
         )
#mpf.show()

"""
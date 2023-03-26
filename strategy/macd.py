import pandas as pd
from storage import upset,query
from datetime import datetime,timedelta
from storage import read
import talib as ta

"""
cross：
(down) bar.pre > 0 & bar.nxt <0  T(bar.pre)=1,T(bar.nxt)=-1
(up)   bar.pre < 0 & bar.nxt >0  T(bar.pre)=-1,T(bar.nxt)=1
turn：
(bottom) diff.pre > diff.mid & diff.nxt > diff.mid T(diff.pre)=-2,T(diff.mid)=-3,T(diff.nxt)=-2
(top) diff.pre < diff.mid & diff.nxt < diff.mid T(diff.pre)=2,T(diff.mid)=3,T(diff.nxt)=2

(bottom reverse) 
1. diff < 0 & dea < 0
2. point sequence: -3,-3
3. point(-3)[0].diff < point(-3)[1].diff
4. point(-3)[0].low > point(-3)[1].low
"""


def mark_data(stock_code, klt=101, start=datetime(2020, 1, 1)):
    k_data = read(stock_code, klt=klt, beg=start, field='open,high,low,close,volume,datetime')
    if len(k_data) < 50:
        return k_data
    k_data.set_index('datetime', drop=True, inplace=True)
    diff, dea, bar = ta.MACD(k_data.close, fastperiod=12, slowperiod=26, signalperiod=9)
    k_data['diff'] = diff
    k_data['dea'] = dea
    k_data['bar'] = bar * 2
    k_data['mark'] = 0
    k_data['signal'] = 0
    s = len(k_data) - 2
    for i in range(1, s):
        bar_pre = k_data.iloc[i - 1]['bar']
        bar_cur = k_data.iloc[i]['bar']
        if bar_pre < 0 and bar_cur > 0:
            k_data.iloc[i - 1, k_data.columns.get_loc('mark')] = -1
            k_data.iloc[i, k_data.columns.get_loc('mark')] = 1
        if bar_pre > 0 and bar_cur < 0:
            k_data.iloc[i - 1, k_data.columns.get_loc('mark')] = 1
            k_data.iloc[i, k_data.columns.get_loc('mark')] = -1

        diff_cur = k_data.iloc[i]['diff']
        diff_pre = k_data.iloc[i - 1]['diff']
        diff_nxt = k_data.iloc[i + 1]['diff']
        if bar_cur < 0 and diff_pre > diff_cur and diff_nxt > diff_cur:
            k_data.iloc[i - 1, k_data.columns.get_loc('mark')] = -2
            k_data.iloc[i, k_data.columns.get_loc('mark')] = -3
            k_data.iloc[i + 1, k_data.columns.get_loc('mark')] = -2
        if bar_cur > 0 and diff_pre < diff_cur and diff_nxt < diff_cur:
            k_data.iloc[i - 1, k_data.columns.get_loc('mark')] = 2
            k_data.iloc[i, k_data.columns.get_loc('mark')] = 3
            k_data.iloc[i + 1, k_data.columns.get_loc('mark')] = 2

    k_mark = k_data[abs(k_data['mark']) == 3]

    s2 = len(k_mark)-1
    for i in range(1, s2):
        mark_pre = k_mark.iloc[i - 1]['mark']
        mark_cur = k_mark.iloc[i]['mark']
        if mark_pre == 3 and mark_cur == 3:
            if k_mark.iloc[i - 1]['high'] >= k_mark.iloc[i]['high']:
                k_mark.iloc[i, k_mark.columns.get_loc('mark')] = 2
            else:
                k_mark.iloc[i - 1, k_mark.columns.get_loc('mark')] = 2
        # 震荡
        if mark_cur == 3 and k_mark.iloc[i]['diff'] > -0.1:
            k_mark.iloc[i, k_mark.columns.get_loc('mark')] = 1

    #k_mark.to_csv('k_mark_{}.csv'.format(stock_code))

    k_mark_new = k_mark[abs(k_mark['mark']) == 3]
    return k_mark_new


def bottom_reverse(k_mark):
    size = len(k_mark)
    for i in range(2,size):
        mark_2 = k_mark.iloc[i-2, k_mark.columns.get_loc('mark')]
        mark_1 = k_mark.iloc[i-1, k_mark.columns.get_loc('mark')]
        mark_0 = k_mark.iloc[i, k_mark.columns.get_loc('mark')]
        bar0 = k_mark.iloc[i, k_mark.columns.get_loc('bar')]
        if mark_2 == -3 and mark_1 == 3 and mark_0 == -3 and abs(bar0) > 0.1:
            diff2 = k_mark.iloc[i - 2, k_mark.columns.get_loc('diff')]
            diff1 = k_mark.iloc[i - 1, k_mark.columns.get_loc('diff')]
            diff0 = k_mark.iloc[i, k_mark.columns.get_loc('diff')]
            low2 = k_mark.iloc[i - 2, k_mark.columns.get_loc('low')]
            low0 = k_mark.iloc[i, k_mark.columns.get_loc('low')]
            if diff1 < 0 and diff2 < diff0 and low2 > low0:
                k_mark.iloc[i, k_mark.columns.get_loc('signal')] = 1
    k_signal = k_mark[k_mark['signal'] == 1]

    #k_signal.to_csv('k_signal.csv')
    return k_signal


def search(stocks=[], lit=-7):
    sql = 'SELECT code FROM `all_realtime`'
    if len(stocks)>0:
        sql = '{} WHERE code IN({})'.format(sql,','.join(stocks))
    codes = query(sql)
    t1 = datetime.now()
    print('开始时间：{},记录数:{}'.format(t1, len(codes)))
    for idx, row in codes.iterrows():
        data = mark_data(row.code)
        lately = datetime.now()+timedelta(days=lit)
        if len(data) > 0:
            signal = bottom_reverse(data)
            if len(signal) > 0:
                for i, row2 in signal.iterrows():
                    if datetime.strptime(i, '%Y-%m-%d') > lately:
                        print('[编码]{}，[日期]{}，[价格]{}'.format(row.code, i, row2.close))
                        s1 = pd.DataFrame({'code': [row.code], 'datetime': [i], 'close': [row2.close], 'create': [datetime.now().strftime('%H %M %S')]})
                        s1.to_csv('macd_result_{}.csv'.format(datetime.now().strftime('%Y%m%d')),index=False, header=False, mode='a')
    t2 = datetime.now()
    print('开始时间：{}, 结束时间:{} , 一共用时：{}分钟'.format(t1, t2, (t2-t1).seconds/60))

stocks=['603291','301096','300842']
search(stocks)
'''
codes = query('SELECT code FROM `all_realtime`')
for idx, row in codes.iterrows():
    print('{} query code {}'.format(idx, row.code))
    sql = 'SELECT datetime FROM `k_{}` WHERE CLOSE IS NULL '.format(row.code)
    data = query(sql)
    if len(data) > 0:
        print('{} error code {}'.format(idx, row.code))
'''
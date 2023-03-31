import storage.kline as kl
import storage.database as db
import talib as ta
import pandas as pd


def mark(stock_code):
    table_name = 'm_{}'.format(stock_code)
    k_data = kl.read(stock_code)
    #k_data.set_index('datetime', drop=True, inplace=True)
    close = k_data.close
    ema_12 = ta.EMA(close, timeperiod=12)
    ema_26 = ta.EMA(close, timeperiod=26)
    diff = ema_12 - ema_26
    dea_9 = ta.EMA(diff, timeperiod=9)
    m_data = pd.concat([k_data.datetime, close, k_data.open, k_data.high, k_data.low, ema_12, ema_26, dea_9], axis=1)
    m_data.columns = ['datetime', 'close', 'open', 'high', 'low', 'ma12', 'ma26', 'dea_9']
    m_data.fillna(0, inplace=True)
    return m_data
    #db.create(table_name)
    #db.insert(m_data, table_name)

def get_macd(stock_code):
    k_data = kl.read(stock_code)
    if len(k_data) == 0:
        return
    k_data['ema12'] = 0
    k_data['ema26'] = 0
    k_data['dea9'] = 0

    ema12, ema26, dea9 = [], [], []
    for i, row in k_data.iterrows():
        close = row['close']
        if i == 0:
            ema12.append(close)
            ema26.append(close)
            dea9.append(close)
        else:
            ema_1 = ema12[-1] * (11/13) + close * (2/13)
            ema_2 = ema26[-1] * (25/27) + close * (2/27)
            dea = dea9[-1] * (8/10) + (ema_1 - ema_2) * (2/10)
            ema12.append(ema_1)
            ema26.append(ema_2)
            dea9.append(dea)

        k_data.loc[i, 'ema12'] = ema12[-1]
        k_data.loc[i, 'ema26'] = ema26[-1]
        k_data.loc[i, 'dea9'] = dea9[-1]
    return k_data


df1 = mark('000600')
df1.to_csv('ta_macd.csv')
df2 = get_macd('000600')
df2.to_csv('my_macd.csv')
from kline import read_data
import database as db


def mark_macd(stock_code,klt=101,begin=''):
    k_data = read_data(stock_code,begin=begin)
    if len(k_data) == 0:
        return

    ema5, ema12, ema26, dea4, dea9 = [], [], [], [], []
    for i, row in k_data.iterrows():
        close = row['close']
        dt = row['datetime']
        if i == 0:
            ema5.append(close)
            ema12.append(close)
            ema26.append(close)
            dea4.append(0)
            dea9.append(0)
        else:
            ema_5 = ema12[-1] * (4 / 6) + close * (2 / 6)
            ema_12 = ema12[-1] * (11 / 13) + close * (2 / 13)
            ema_26 = ema26[-1] * (25 / 27) + close * (2 / 27)
            dea_4 = dea4[-1] * (3 / 5) + (ema_5 - ema_12) * (2 / 5)
            dea_9 = dea9[-1] * (8 / 10) + (ema_12 - ema_26) * (2 / 10)
            ema12.append(ema_12)
            ema26.append(ema_26)
            dea4.append(dea_4)
            dea9.append(dea_9)
        update_sql = "UPDATE `{}` SET `ema5` = '{}', `ema12` = '{}', `ema26` = '{}', `dea4` = '{}', `dea9` = '{}' WHERE `datetime` = '{}' AND `klt` = {} ;"\
            .format(stock_code, ema5[-1],ema12[-1],ema26[-1],dea4[-1],dea9[-1],dt,101)
        db.execute(update_sql)

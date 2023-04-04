from storage.kline import read_mark
from storage.agu import reverse_signal
import storage.database as db


def signal(stock_code, klt=101, begin=''):
    k_mark = read_mark(stock_code, klt=klt, begin=begin)
    size = len(k_mark)
    if size > 3:
        for i in range(2, size):
            mark_2 = k_mark.iloc[i - 2, k_mark.columns.get_loc('mark')]
            mark_1 = k_mark.iloc[i - 1, k_mark.columns.get_loc('mark')]
            mark_0 = k_mark.iloc[i, k_mark.columns.get_loc('mark')]
            if (mark_2 == -3) and (mark_1 == 3) and (mark_0 == -3):
                diff2 = k_mark.iloc[i - 2, k_mark.columns.get_loc('ema12')] - k_mark.iloc[
                    i - 2, k_mark.columns.get_loc('ema26')]
                diff1 = k_mark.iloc[i - 1, k_mark.columns.get_loc('ema12')] - k_mark.iloc[
                    i - 1, k_mark.columns.get_loc('ema26')]
                diff0 = k_mark.iloc[i, k_mark.columns.get_loc('ema12')] - k_mark.iloc[
                    i, k_mark.columns.get_loc('ema26')]
                dt2 = k_mark.iloc[i - 2, k_mark.columns.get_loc('datetime')]
                low2 = find_lowest(stock_code, klt, dt2, k_mark.iloc[i - 2, k_mark.columns.get_loc('low')])
                dt0 = k_mark.iloc[i, k_mark.columns.get_loc('datetime')]
                low0 = find_lowest(stock_code, klt, dt0, k_mark.iloc[i, k_mark.columns.get_loc('low')])
                if diff1 < 0 and diff2 < diff0 and low2 > low0:
                    high1 = k_mark.iloc[i - 1, k_mark.columns.get_loc('high')]
                    if ((high1 - low2) / low2) > 0.1 and ((high1 - low0) / high1) > 0.1:
                        reverse_signal(stock_code, klt, mark_0, dt0)


def find_lowest(stock_code, klt, dt, low):
    lowest = low
    sql_pre = "SELECT low,mark FROM `{}` WHERE klt={} AND `datetime` < '{}' ORDER BY `datetime` DESC LIMIT 10".format(
        stock_code, klt, dt)
    df_pre = db.query(sql_pre)
    for i, row in df_pre.iterrows():
        if row['mark'] > 0:
            break
        else:
            if row['low'] < lowest:
                lowest = row['low']
    sql_nex = "SELECT low,mark FROM `{}` WHERE klt={} AND `datetime` > '{}' ORDER BY `datetime` LIMIT 10".format(
        stock_code, klt, dt)
    df_nex = db.query(sql_nex)
    for i, row in df_nex.iterrows():
        if row['mark'] > 0:
            break
        else:
            if row['low'] < lowest:
                lowest = row['low']
    return lowest

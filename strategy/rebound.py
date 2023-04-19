import storage.database as db
from datetime import datetime


def search_signal(stock_code, klt, tip=False):
    k_mark = db.read_mark_data(stock_code, klt=klt, mark='-3,3')
    zf = get_zf(klt)
    size = len(k_mark)
    if size > 2:
        for i in range(2, size):
            bar2 = k_mark.iloc[i - 2, k_mark.columns.get_loc('bar')]
            bar1 = k_mark.iloc[i - 1, k_mark.columns.get_loc('bar')]
            bar0 = k_mark.iloc[i, k_mark.columns.get_loc('bar')]
            if klt in [101, 102]:
                if abs(bar2) < 1 and abs(bar1) < 1 and abs(bar0) < 1:
                    continue
            '''else:
                if abs(bar2) < 0.1 and abs(bar1) < 0.1 and abs(bar0) < 0.1:
                    continue'''

            mark_2 = k_mark.iloc[i - 2, k_mark.columns.get_loc('mark')]
            mark_1 = k_mark.iloc[i - 1, k_mark.columns.get_loc('mark')]
            mark_0 = k_mark.iloc[i, k_mark.columns.get_loc('mark')]
            if (mark_2 == -3) and (mark_1 == 3) and (mark_0 == -3):
                diff2 = k_mark.iloc[i - 2, k_mark.columns.get_loc('diff')]
                diff1 = k_mark.iloc[i - 1, k_mark.columns.get_loc('diff')]
                diff0 = k_mark.iloc[i, k_mark.columns.get_loc('diff')]
                low2 = k_mark.iloc[i - 2, k_mark.columns.get_loc('low')]
                low0 = k_mark.iloc[i, k_mark.columns.get_loc('low')]
                if (diff1 < 0) and (diff2 < diff0) and (low2 > low0):
                    high1 = k_mark.iloc[i - 1, k_mark.columns.get_loc('high')]
                    if ((high1 - low2) / low2) > zf and ((high1 - low0) / high1) > zf:
                        dt2 = k_mark.iloc[i - 2, k_mark.columns.get_loc('datetime')]
                        dt0 = k_mark.iloc[i, k_mark.columns.get_loc('datetime')]
                        low0 = find_lowest(stock_code, klt, dt0, k_mark.iloc[i, k_mark.columns.get_loc('low')])
                        if low0 < 0:
                            continue
                        low2 = find_lowest(stock_code, klt, dt2, k_mark.iloc[i - 2, k_mark.columns.get_loc('low')])
                        if (diff1 < 0) and (diff2 < diff0) and (low2 > low0) and ((high1 - low2) / low2) > zf and (
                                (high1 - low0) / high1) > zf:
                            if watch:
                                db.add_watch(stock_code, klt, mark_0, dt0)
                                print('{} [add watcher] code:{}, klt:{}, signal:{}, datetime:{}'.format(
                                    datetime.now().strftime('%Y-%m-%d %H:%M'), stock_code, klt, mark_0, dt0))
                            else:
                                db.save_signal(stock_code, klt, mark_0, dt0)
                                print('{} [save signal] code:{}, klt:{}, signal:{}, datetime:{}'.format(
                                    datetime.now().strftime('%Y-%m-%d %H:%M'), stock_code, klt, mark_0, dt0))

            if (mark_2 == 3) and (mark_1 == -3) and (mark_0 == 3):
                diff2 = k_mark.iloc[i - 2, k_mark.columns.get_loc('diff')]
                diff1 = k_mark.iloc[i - 1, k_mark.columns.get_loc('diff')]
                diff0 = k_mark.iloc[i, k_mark.columns.get_loc('diff')]
                high2 = k_mark.iloc[i - 2, k_mark.columns.get_loc('high')]
                high0 = k_mark.iloc[i, k_mark.columns.get_loc('high')]
                if (diff0 > 0) and (diff1 > 0) and (diff2 > diff0) and (high2 < high0):
                    low1 = k_mark.iloc[i - 1, k_mark.columns.get_loc('low')]
                    if ((high2 - low1) / high2) > zf and ((high0 - low1) / high0) > zf:
                        dt2 = k_mark.iloc[i - 2, k_mark.columns.get_loc('datetime')]
                        dt0 = k_mark.iloc[i, k_mark.columns.get_loc('datetime')]
                        high0 = find_highest(stock_code, klt, dt0, k_mark.iloc[i, k_mark.columns.get_loc('high')])
                        if high0 < 0:
                            continue
                        high2 = find_highest(stock_code, klt, dt2, k_mark.iloc[i - 2, k_mark.columns.get_loc('high')])
                        if (diff0 > 0) and (diff1 > 0) and (diff2 > diff0) and (high2 < high0) and (
                                (high2 - low1) / high2) > zf and ((high0 - low1) / high0) > zf:
                            db.save_signal(stock_code, klt, mark_0, dt0, tip)
                            print('{} [save signal {}] code:{}, klt:{}, signal:{}, datetime:{}'.format(
                                    datetime.now().strftime('%Y-%m-%d %H:%M'), tip, stock_code, klt, mark_0, dt0))


def get_zf(klt):
    if klt > 100:
        return 0.1
    if klt == 60:
        return 0.03
    else:
        return 0.01


def find_lowest(stock_code, klt, dt, low):
    lowest = low
    mark_size = 0
    sql_pre = "SELECT low,mark FROM `{}` WHERE klt={} AND `datetime` < '{}' ORDER BY `datetime` DESC LIMIT 10".format(
        stock_code, klt, dt)
    df_pre = db.query(sql_pre)
    for i, row in df_pre.iterrows():
        if row['mark'] > 0:
            break
        else:
            mark_size = mark_size + 1
            if row['low'] < lowest:
                lowest = row['low']
    sql_nex = "SELECT low,mark FROM `{}` WHERE klt={} AND `datetime` > '{}' ORDER BY `datetime` LIMIT 10".format(
        stock_code, klt, dt)
    df_nex = db.query(sql_nex)
    for i, row in df_nex.iterrows():
        if row['mark'] > 0:
            break
        else:
            mark_size = mark_size + 1
            if row['low'] < lowest:
                lowest = row['low']
    if (mark_size < 3) and (mark_size > 12):
        return -1
    else:
        return lowest


def find_highest(stock_code, klt, dt, high):
    highest = high
    mark_size = 0
    sql_pre = "SELECT high,mark FROM `{}` WHERE klt={} AND `datetime` < '{}' ORDER BY `datetime` DESC LIMIT 10".format(
        stock_code, klt, dt)
    df_pre = db.query(sql_pre)
    for i, row in df_pre.iterrows():
        if row['mark'] < 0:
            break
        else:
            mark_size = mark_size + 1
            if row['high'] > highest:
                highest = row['high']
    sql_nex = "SELECT high,mark FROM `{}` WHERE klt={} AND `datetime` > '{}' ORDER BY `datetime` LIMIT 10".format(
        stock_code, klt, dt)
    df_nex = db.query(sql_nex)
    for i, row in df_nex.iterrows():
        if row['mark'] < 0:
            break
        else:
            mark_size = mark_size + 1
            if row['high'] > highest:
                highest = row['high']
    if (mark_size < 3) and (mark_size > 12):
        return -1
    else:
        return highest


if __name__ == '__main__':
    code_dict = db.query("SELECT `code`, `status` FROM `code_dict`")
    for i, row in code_dict.iterrows():
        code = row['code']
        for klt in [101, 102]:
            search_signal(code, klt)

import storage.kline as kl
import storage.database as db
from datetime import datetime, timedelta
import logging


def update_mark(code, klt):
    begin_date = db.get_begin_datetime(code, klt, mark=True)
    k_data = db.read_kline_data(code, klt=klt, begin=begin_date)
    size = len(k_data)
    print('{} [update mark] code:{}, klt:{}, begin:{}, size:{}'.format(datetime.now().strftime('%Y-%m-%d %H:%M'), code, klt, begin_date, size))
    if size == 0:
        return

    ema5, ema12, ema26, dea4, dea9 = [], [], [], [], []
    dt, diff, bar = [], [], []
    u_sql = db.get_sql('update_indicator.sql').format(code, klt)
    m_sql = db.get_sql('update_mark.sql').format(code, klt)
    i_list = []
    m_list = []
    for i, row in k_data.iterrows():
        close = row['close']
        dt.append(row['datetime'])

        if i == 0:
            ema_5 = close
            ema_12 = close
            ema_26 = close
            dea_4 = 0
            dea_9 = 0
            pre_data = db.read_kline_data(code, klt=klt, end=begin_date, limit=2, order_by='`datetime` DESC')
            if (len(pre_data) == 2) and (pre_data.loc[1, 'ema5'] is not None) and (pre_data.loc[1, 'ema5'] > 0.0):
                ema_5 = pre_data.loc[1, 'ema5'] * (4 / 6) + close * (2 / 6)
                ema_12 = pre_data.loc[1, 'ema12'] * (11 / 13) + close * (2 / 13)
                ema_26 = pre_data.loc[1, 'ema26'] * (25 / 27) + close * (2 / 27)
                dea_4 = pre_data.loc[1, 'dea4'] * (3 / 5) + (ema_5 - ema_12) * (2 / 5)
                dea_9 = pre_data.loc[1, 'dea9'] * (8 / 10) + (ema_12 - ema_26) * (2 / 10)
        else:
            ema_5 = ema5[-1] * (4 / 6) + close * (2 / 6)
            ema_12 = ema12[-1] * (11 / 13) + close * (2 / 13)
            ema_26 = ema26[-1] * (25 / 27) + close * (2 / 27)
            dea_4 = dea4[-1] * (3 / 5) + (ema_5 - ema_12) * (2 / 5)
            dea_9 = dea9[-1] * (8 / 10) + (ema_12 - ema_26) * (2 / 10)

        ema5.append(ema_5)
        ema12.append(ema_12)
        ema26.append(ema_26)
        dea4.append(dea_4)
        dea9.append(dea_9)
        diff.append(ema_12 - ema_26)
        bar.append(ema_12 - ema_26 - dea_9)

        init_mark = 1 if bar[-1] > 0 else -1
        i_list.append((ema5[-1],
                       ema12[-1],
                       ema26[-1],
                       dea4[-1],
                       dea9[-1],
                       init_mark,
                       dt[-1]))

        if (len(i_list) > 100) or ((i + 1) == size):
            db.execute(db.get_connect(code), u_sql, many=True, lis=i_list)
            i_list.clear()

        mark2 = mark_2(diff, bar)
        if abs(mark2) == 2:
            m_list.append((mark2, dt[i - 1]))

        if ((bar[i] > 0) and (bar[i - 1] < 0)) or ((bar[i] < 0) and (bar[i - 1] > 0)):
            m3_idx, m3_val = mark_3(diff[:i], bar[:i])
            if m3_idx > 0:
                m_list.append((m3_val, dt[m3_idx]))

        if (len(m_list) > 100) or ((i + 1) == size):
            db.execute(db.get_connect(code), m_sql, many=True, lis=m_list)
            m_list.clear()

    print('{} [mark done] code:{}, klt:{}, size:{}'.format(datetime.now().strftime('%Y-%m-%d %H:%M'), code, klt, size))
    return size


def save_signal(stock_code, klt, watch=False):
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
                                print('{} [add watcher] code:{}, klt:{}, signal:{}, datetime:{}'.format(datetime.now().strftime('%Y-%m-%d %H:%M'), stock_code, klt, mark_0, dt0))
                            else:
                                db.save_signal(stock_code, klt, mark_0, dt0)
                                print('{} [save signal] code:{}, klt:{}, signal:{}, datetime:{}'.format(datetime.now().strftime('%Y-%m-%d %H:%M'), stock_code, klt, mark_0, dt0))

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
                            if watch:
                                db.add_watch(stock_code,klt,mark_0, dt0)
                                print('{} [add watcher] code:{}, klt:{}, signal:{}, datetime:{}'.format(datetime.now().strftime('%Y-%m-%d %H:%M'), stock_code, klt, mark_0, dt0))
                            else:
                                db.save_signal(stock_code, klt, mark_0, dt0)
                                print('{} [save signal] code:{}, klt:{}, signal:{}, datetime:{}'.format(datetime.now().strftime('%Y-%m-%d %H:%M'), stock_code, klt, mark_0, dt0))


# def macd_mark(stock_code, klt, begin):
#     begin = get_begin_date(klt, begin)
#     logging.debug('[update mark] code:{}, klt:{}, begin:{}'.format(stock_code, klt, begin))
#     k_data = read_data(stock_code, klt=klt, begin=begin)
#     if len(k_data) == 0:
#         return
#
#     ema5, ema12, ema26, dea4, dea9 = [], [], [], [], []
#     dt, diff, bar = [], [], []
#     size = len(k_data)
#     for i, row in k_data.iterrows():
#         close = row['close']
#         dt.append(row['datetime'])
#
#         if i == 0:
#             ema_5 = close
#             ema_12 = close
#             ema_26 = close
#             dea_4 = 0
#             dea_9 = 0
#             if begin != '':
#                 pre_data = read_data(stock_code, klt=klt, end=begin, limit=2, order_by='`datetime` DESC')
#                 if (len(pre_data) == 2) and (pre_data.loc[1, 'ema5'] is not None) and (pre_data.loc[1, 'ema5'] > 0.0):
#                     ema_5 = pre_data.loc[1, 'ema5'] * (4 / 6) + close * (2 / 6)
#                     ema_12 = pre_data.loc[1, 'ema12'] * (11 / 13) + close * (2 / 13)
#                     ema_26 = pre_data.loc[1, 'ema26'] * (25 / 27) + close * (2 / 27)
#                     dea_4 = pre_data.loc[1, 'dea4'] * (3 / 5) + (ema_5 - ema_12) * (2 / 5)
#                     dea_9 = pre_data.loc[1, 'dea9'] * (8 / 10) + (ema_12 - ema_26) * (2 / 10)
#         else:
#             ema_5 = ema5[-1] * (4 / 6) + close * (2 / 6)
#             ema_12 = ema12[-1] * (11 / 13) + close * (2 / 13)
#             ema_26 = ema26[-1] * (25 / 27) + close * (2 / 27)
#             dea_4 = dea4[-1] * (3 / 5) + (ema_5 - ema_12) * (2 / 5)
#             dea_9 = dea9[-1] * (8 / 10) + (ema_12 - ema_26) * (2 / 10)
#
#         ema5.append(ema_5)
#         ema12.append(ema_12)
#         ema26.append(ema_26)
#         dea4.append(dea_4)
#         dea9.append(dea_9)
#         diff.append(ema_12 - ema_26)
#         bar.append(ema_12 - ema_26 - dea_9)
#
#         init_mark = 1 if bar[-1] > 0 else -1
#         update_sql = "UPDATE `{0}` SET `ema5` = '{1}', `ema12` = '{2}', `ema26` = '{3}', `dea4` = '{4}', `dea9` = '{5}', " \
#                      "`mark` = '{6}' WHERE `datetime` = '{7}' AND `klt` = {8} ; " \
#             .format(stock_code,
#                     ema5[-1], ema12[-1], ema26[-1], dea4[-1], dea9[-1],
#                     init_mark, dt[-1], klt)
#         db.execute(db.get_connect(stock_code), 'update_indicator.sql', stock_code,
#                    ema5[-1], ema12[-1], ema26[-1], dea4[-1], dea9[-1],
#                    init_mark, dt[-1], klt)
#
#         # db.execute(update_sql)
#
#         mark2 = mark_2(diff, bar)
#         if abs(mark2) == 2:
#             update_sql2 = "UPDATE `{0}` SET `mark` = '{1}' WHERE `datetime` = '{2}' AND `klt` = {3} ;" \
#                 .format(stock_code, mark2, dt[i - 1], klt)
#             db.execute(db.get_connect(stock_code), update_sql2)
#
#         if ((bar[i] > 0) and (bar[i - 1] < 0) or (bar[i] < 0) and (bar[i - 1] > 0)):
#             m3_idx, m3_val = mark_3(diff[:i], bar[:i])
#             if m3_idx > 0:
#                 update_sql3 = "UPDATE `{0}` SET `mark` = '{1}' WHERE `datetime` = '{2}' AND `klt` = {3} ;" \
#                     .format(stock_code, m3_val, dt[m3_idx], klt)
#                 db.execute(db.get_connect(stock_code), update_sql3)
#     print('[update mark done] code:{}, result:{}'.format(stock_code, size))


# def macd_mark2(stock_code, klt, begin):
#     begin = get_begin_date(klt, begin)
#     logging.debug('[update mark] code:{}, klt:{}, begin:{}'.format(stock_code, klt, begin))
#     k_data = read_data(stock_code, klt=klt, begin=begin)
#     if len(k_data) == 0:
#         return
#
#     ema5, ema12, ema26, dea4, dea9 = [], [], [], [], []
#     dt, diff, bar = [], [], []
#     size = len(k_data)
#     for i, row in k_data.iterrows():
#         close = row['close']
#         dt.append(row['datetime'])
#
#         if i == 0:
#             ema_5 = close
#             ema_12 = close
#             ema_26 = close
#             dea_4 = 0
#             dea_9 = 0
#             if begin != '':
#                 pre_data = read_data(stock_code, klt=klt, end=begin, limit=2, order_by='`datetime` DESC')
#                 if (len(pre_data) == 2) and (pre_data.loc[1, 'ema5'] is not None) and (pre_data.loc[1, 'ema5'] > 0.0):
#                     ema_5 = pre_data.loc[1, 'ema5'] * (4 / 6) + close * (2 / 6)
#                     ema_12 = pre_data.loc[1, 'ema12'] * (11 / 13) + close * (2 / 13)
#                     ema_26 = pre_data.loc[1, 'ema26'] * (25 / 27) + close * (2 / 27)
#                     dea_4 = pre_data.loc[1, 'dea4'] * (3 / 5) + (ema_5 - ema_12) * (2 / 5)
#                     dea_9 = pre_data.loc[1, 'dea9'] * (8 / 10) + (ema_12 - ema_26) * (2 / 10)
#         else:
#             ema_5 = ema5[-1] * (4 / 6) + close * (2 / 6)
#             ema_12 = ema12[-1] * (11 / 13) + close * (2 / 13)
#             ema_26 = ema26[-1] * (25 / 27) + close * (2 / 27)
#             dea_4 = dea4[-1] * (3 / 5) + (ema_5 - ema_12) * (2 / 5)
#             dea_9 = dea9[-1] * (8 / 10) + (ema_12 - ema_26) * (2 / 10)
#
#         ema5.append(ema_5)
#         ema12.append(ema_12)
#         ema26.append(ema_26)
#         dea4.append(dea_4)
#         dea9.append(dea_9)
#         diff.append(ema_12 - ema_26)
#         bar.append(ema_12 - ema_26 - dea_9)
#
#         init_mark = 1 if bar[-1] > 0 else -1
#         update_sql = "UPDATE `{0}` SET `ema5` = '{1}', `ema12` = '{2}', `ema26` = '{3}', `dea4` = '{4}', `dea9` = '{5}', " \
#                      "`mark` = '{6}' WHERE `datetime` = '{7}' AND `klt` = {8} ; " \
#             .format(stock_code,
#                     ema5[-1], ema12[-1], ema26[-1], dea4[-1], dea9[-1],
#                     init_mark, dt[-1], klt)
#         db.execute2(update_sql)
#
#         mark2 = mark_2(diff, bar)
#         if abs(mark2) == 2:
#             update_sql2 = "UPDATE `{0}` SET `mark` = '{1}' WHERE `datetime` = '{2}' AND `klt` = {3} ;" \
#                 .format(stock_code, mark2, dt[i - 1], klt)
#             db.execute2(update_sql2)
#
#         if ((bar[i] > 0) and (bar[i - 1] < 0) or (bar[i] < 0) and (bar[i - 1] > 0)):
#             m3_idx, m3_val = mark_3(diff[:i], bar[:i])
#             if m3_idx > 0:
#                 update_sql3 = "UPDATE `{0}` SET `mark` = '{1}' WHERE `datetime` = '{2}' AND `klt` = {3} ;" \
#                     .format(stock_code, m3_val, dt[m3_idx], klt)
#                 db.execute2(update_sql3)
#     print('[update mark done] code:{}, result:{}'.format(stock_code, size))


# def get_begin_date(klt, begin_date):
#     y = datetime.now().year
#     m = datetime.now().month
#     d = datetime.now().day
#     # begin_date = datetime.strptime(begin, '%Y-%m-%d')
#     if klt == 102:
#         earliest = datetime((y - 3), m, d)
#     elif klt == 101:
#         earliest = datetime((y - 1), m, d)
#     elif klt == 60:
#         earliest = datetime.now() - timedelta(days=15)
#     else:
#         earliest = datetime.now() - timedelta(days=5)
#
#     if (begin_date is None) or (begin_date < earliest):
#         return earliest.strftime('%Y-%m-%d')
#     else:
#         return begin_date.strftime('%Y-%m-%d')


# 拐点
def mark_2(diff, bar):
    m = 0
    s = len(diff)
    if s > 2:
        bar_1, bar_2, bar_3 = bar[s - 3], bar[s - 2], bar[s - 1]
        diff_1, diff_2, diff_3 = diff[s - 3], diff[s - 2], diff[s - 1]
        if (bar_1 < 0.0) and (bar_2 < 0.0) and (bar_3 < 0.0):
            if (diff_1 > diff_2) and (diff_2 < diff_3):
                m = -2
        if (bar_1 > 0.0) and (bar_2 > 0.0) and (bar_3 > 0.0):
            if (diff_1 < diff_2) and (diff_2 > diff_3):
                m = 2
    return m


# 极值点
def mark_3(diff, bar):
    m_idx = -1
    m_val = 0
    s = len(diff)
    i = s - 1
    b = bar[i]
    if b < 0.0:
        m_idx, m_val = i, diff[i]
        i = i - 1
        while i > 0:
            if bar[i] > 0.0:
                break
            else:
                if diff[i] < m_val:
                    m_idx, m_val = i, diff[i]
            i = i - 1
        if m_idx == (s - 1):
            m_idx = -1
        else:
            m_val = -3
    if b > 0.0:
        m_idx, m_val = i, diff[i]
        i = i - 1
        while i > 0:
            if bar[i] < 0.0:
                break
            else:
                if diff[i] > m_val:
                    m_idx, m_val = i, diff[i]
            i = i - 1
        if m_idx == (s - 1):
            m_idx = -1
        else:
            m_val = 3

    return m_idx, m_val


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
    pass

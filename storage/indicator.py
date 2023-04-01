from kline import read_data
import database as db


def update(stock_code,klt=101,begin=''):
    k_data = read_data(stock_code,begin=begin)
    if len(k_data) == 0:
        return

    ema5, ema12, ema26, dea4, dea9 = [], [], [], [], []
    dt, diff, bar, low, high = [], [], [], [], []
    for i, row in k_data.iterrows():
        close = row['close']
        low.append(row['low'])
        high.append(row['high'])
        dt.append(row['datetime'])
        if i == 0:
            ema5.append(close)
            ema12.append(close)
            ema26.append(close)
            dea9.append(0)
            diff.append(0)
            bar.append(0)
        else:
            ema_5 = ema12[-1] * (4 / 6) + close * (2 / 6)
            ema_12 = ema12[-1] * (11 / 13) + close * (2 / 13)
            ema_26 = ema26[-1] * (25 / 27) + close * (2 / 27)
            dea_4 = dea4[-1] * (3 / 5) + (ema_5 - ema_12) * (2 / 5)
            dea_9 = dea9[-1] * (8 / 10) + (ema_12 - ema_26) * (2 / 10)
            ema5.append(ema_5)
            ema12.append(ema_12)
            ema26.append(ema_26)
            dea4.append(dea_4)
            dea9.append(dea_9)
            diff.append(ema_12-ema_26)
            bar.append(ema_12-ema_26-dea_9)

        init_mark = -1 if bar[-1] > 0 else 1
        update_sql = "UPDATE `{0}` SET `ema5` = '{1}', `ema12` = '{2}', `ema26` = '{3}', `dea4` = '{4}', `dea9` = '{5}', " \
                     "`mark` = '{6}' WHERE `datetime` = '{7}' AND `klt` = {8} ; " \
            .format(stock_code,
                    ema5[-1], ema12[-1], ema26[-1], dea4[-1], dea9[-1],
                    init_mark, dt, 101)
        db.execute(update_sql)

        mark2 = mark_2(diff, bar)
        if abs(mark2) == 2:
            update_sql2 = "UPDATE `{0}` SET `mark` = '{1}' WHERE `datetime` = '{2}' AND `klt` = {3} ;"\
                .format(stock_code, mark2, dt[i-1], klt)
            db.execute(update_sql2)

        m3_idx, m3_val = mark_3(diff,bar)
        if m3_idx > 0:
            update_sql3 = "UPDATE `{0}` SET `mark` = '{1}' WHERE `datetime` = '{2}' AND `klt` = {3} ;" \
                .format(stock_code, m3_val, dt[m3_idx], klt)
            db.execute(update_sql3)


# 拐点
def mark_2(diff, bar):
    m = 0
    s = len(diff)
    if s > 2:
        bar_1, bar_2, bar_3 = bar[s-2], bar[s-1], bar[s]
        diff_1, diff_2, diff_3 = diff[s-2], diff[s-1], diff[s]
        if bar_1 < 0 & bar_2 < 0 & bar_3 < 0:
            if diff_1 > diff_2 & diff_2 < diff_3:
                m = -2
        if bar_1 > 0 & bar_2 > 0 & bar_3 > 0:
            if diff_1 < diff_2 & diff_2 > diff_3:
                m = 2
    return m


# 极值点
def mark_3(diff, bar):
    m_idx = -1
    m_val = 0
    s = len(diff)
    i = s-1
    if bar[i] < 0:
        m_idx, m_val = i, diff[i]
        while i > 0:
            if bar[i] > 0:
                break
            else:
                if diff[i] < m_val:
                    m_idx, m_val = i, diff[i]
            i = i-1
        if m_idx == (s - 1):
            m_idx = -1
        else:
            m_val = -3
    if bar[i] > 0:
        m_idx, m_val = i, diff[i]
        while i > 0:
            if bar[i] < 0:
                break
            else:
                if diff[i] > m_val:
                    m_idx, m_val = i, diff[i]
            i = i - 1
        if m_idx == (s - 1):
            m_idx = 1
        else:
            m_val = 3

    return m_idx,m_val
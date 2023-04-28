import storage.database as db
from datetime import datetime
import talib as ta


def update_macd_and_mark(code, klt):
    begin_date = db.get_begin_datetime(code, klt, mark=True)
    k_data = db.read_kline_data(code, klt=klt, begin=begin_date)
    size = len(k_data)
    print('{} [update mark] code:{}, klt:{}, begin:{}, size:{}'.format(datetime.now().strftime('%Y-%m-%d %H:%M'), code,
                                                                       klt, begin_date, size))
    if size == 0:
        return

    ma5, ma10, ma20 = [], [], []
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
            ma_5 = close
            ma_10 = close
            ma_20 = close
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


if __name__ == '__main__':
    pass

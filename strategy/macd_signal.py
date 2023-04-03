from storage.kline import read_mark
from storage.agu import reverse_signal


def signal(stock_code, klt=101, begin=''):
    k_mark = read_mark(stock_code, klt=klt, begin=begin)
    size = len(k_mark)
    if size > 3:
        for i in range(2, size):
            mark_2 = k_mark.iloc[i-2, k_mark.columns.get_loc('mark')]
            mark_1 = k_mark.iloc[i-1, k_mark.columns.get_loc('mark')]
            mark_0 = k_mark.iloc[i, k_mark.columns.get_loc('mark')]
            if (mark_2 == -3) and (mark_1 == 3) and (mark_0 == -3):
                diff2 = k_mark.iloc[i - 2, k_mark.columns.get_loc('ema12')] - k_mark.iloc[i - 2, k_mark.columns.get_loc('ema26')]
                diff1 = k_mark.iloc[i - 1, k_mark.columns.get_loc('ema12')] - k_mark.iloc[i - 1, k_mark.columns.get_loc('ema26')]
                diff0 = k_mark.iloc[i, k_mark.columns.get_loc('ema12')] - k_mark.iloc[i, k_mark.columns.get_loc('ema26')]
                low2 = k_mark.iloc[i - 2, k_mark.columns.get_loc('low')]
                low0 = k_mark.iloc[i, k_mark.columns.get_loc('low')]
                if diff1 < 0 and diff2 < diff0 and low2 > low0:
                    high1 = k_mark.iloc[i - 1, k_mark.columns.get_loc('high')]
                    if ((high1-low2)/low2) > 0.1 and ((high1-low0)/high1) > 0.1:
                        dt = k_mark.iloc[i, k_mark.columns.get_loc('datetime')]
                        reverse_signal(stock_code, klt, mark_0, dt)

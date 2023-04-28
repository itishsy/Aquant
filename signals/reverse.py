import storage.database as db
from objects import Candle, Signal
from typing import List, Callable


# rebound之后的13~21根bar出现的拐点
# abs(bar)

def search_signal(stock_code, klt, start_date, tip=False):
    k_mark = db.read_mark_data(stock_code, klt=klt, begin=start_date)
    size = len(k_mark)
    if size > 2:
        for i in range(10, size):
            bar2 = k_mark.iloc[i - 2, k_mark.columns.get_loc('bar')]
            bar1 = k_mark.iloc[i - 1, k_mark.columns.get_loc('bar')]
            bar0 = k_mark.iloc[i, k_mark.columns.get_loc('bar')]

            mark_2 = k_mark.iloc[i - 2, k_mark.columns.get_loc('mark')]
            mark_1 = k_mark.iloc[i - 1, k_mark.columns.get_loc('mark')]
            mark_0 = k_mark.iloc[i, k_mark.columns.get_loc('mark')]

            if mark_2 > 0 and mark_1 > 0 and mark_0 > 0:
                if bar0 > bar1 and bar2 > bar1:
                    print(k_mark.iloc[i, k_mark.columns.get_loc('datetime')])

            if mark_2 < 0 and mark_1 < 0 and mark_0 > 0:
                print(k_mark.iloc[i, k_mark.columns.get_loc('datetime')])

            if mark_2 > 0 and mark_1 < 0 and mark_0 > 0:
                print(k_mark.iloc[i, k_mark.columns.get_loc('datetime')])


def check_signal(cds: List[Candle]) -> List[Signal]:
    sns = []
    for i in range(1, len(cds)-1):

        pass
    return sns


if __name__ == '__main__':
    candles = db.read_mark_candle(stock_code='300769', klt=101, begin='2023-01-04', mark='3,-3')
    signals = check_signal(candles)
    print(signals)
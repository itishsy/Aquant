import storage.database as db
from datetime import datetime


# rebound之后的13~21根bar出现的拐点
# abs(bar)

def search_signal(stock_code, klt, start_date, tip=False):
    k_mark = db.read_mark_data(stock_code, klt=klt, begin = start_date)
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

            if mark_2 <0 and mark_1 < 0 and mark_0 > 0:
                print(k_mark.iloc[i, k_mark.columns.get_loc('datetime')])

            if mark_2 > 0 and mark_1 < 0 and mark_0 > 0:
                print(k_mark.iloc[i, k_mark.columns.get_loc('datetime')])


# search_signal('300223', 102, '2022-10-28')
# print('============')
# search_signal('002852', 101, '2023-03-17')
# print('============')
search_signal('300769', 101, '2023-01-04')




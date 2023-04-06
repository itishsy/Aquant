import storage.database as db
from storage.fetcher import init_code_dict, fetch_code_dict, fetch_data, update_storage_date
from strategy.macd_signal import signal
from storage.agu import fetch_error

if __name__ == '__main__':
    db.init_schema()
    init_code_dict()
    code_dict = fetch_code_dict()
    for i,row in code_dict.iterrows():
        code = row['code']
        begin_date = ''
        try:
            begin_date = fetch_data(code)
        except Exception as e:
            fetch_size = -1
            fetch_error(code, begin_date, e)
            print('{} fetch {} error: {}'.format(i, code, e))
        else:
            signal(code, klt=102)

            # signal(code, klt=101)

import storage.database as db
from storage.fetcher import fetch_code_dict, fetch_data,update_storage_date
from strategy.macd_signal import signal
from storage.agu import fetch_error
from datetime import datetime

if __name__ == '__main__':
    db.init_schema()
    code_dict = fetch_code_dict()
    for code in code_dict:
        begin_date = ''
        try:
            begin_date = fetch_data(code)
        except Exception as e:
            fetch_size = -1
            fetch_error(code, begin_date, e)
            print('fetch {} error: {}'.format(code, e))
        else:
            signal(code, klt=102)
            signal(code, klt=101)
    update_storage_date(datetime.now().strftime('%Y%m'))

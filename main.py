from datetime import datetime
from storage.fetch import fetch_data, find_active_symbols
from signals.reverse import search_signal
import logging
import config

logging.basicConfig(format='%(asctime)s %(message)s', filename='d://aquant.log'.format(config.work_path))
logging.getLogger().setLevel(logging.INFO)

if __name__ == '__main__':
    start_time = datetime.now()
    sbs = find_active_symbols()
    for sb in sbs:
        fetch_data(sb.code, 102)
        search_signal(sb.code, 102)
        fetch_data(sb.code, 101)
        search_signal(sb.code, 101)
        fetch_data(sb.code, 60)
        search_signal(sb.code, 60)
        fetch_data(sb.code, 30)
    end_time = datetime.now()
    print("==============用時：{}=================".format(end_time - start_time))

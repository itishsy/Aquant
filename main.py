from datetime import datetime
import storage.database as db
from storage.fetcher import fetch_all
import logging
import config

logging.basicConfig(format='%(asctime)s %(message)s', filename='{}/aquant.log'.format(config.work_path))
logging.getLogger().setLevel(logging.INFO)

if __name__ == '__main__':
    db.init_schema()
    start_time = datetime.now()
    fetch_all()
    print("==============用時：{}=================".format(datetime.now() - start_time))
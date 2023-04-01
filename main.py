import storage.database as db
from storage.fetcher import start_fetch
import storage.indicator as idc

if __name__ == '__main__':
    db.init_schema()
    start_fetch()

from engines.engine import job_engine
from models.symbol import Symbol
from datetime import datetime
import candles.fetcher as fet


@job_engine
class Fetcher:

    @staticmethod
    def start():
        now = datetime.now()
        if now.weekday() == 5:
            freq = [103, 102, 101, 120, 60, 30]
            Symbol.fetch()
            fet.fetch_all(freq=freq, clean=True)
        else:
            freq = [101, 120, 60, 30]
            fet.fetch_all(freq=freq)


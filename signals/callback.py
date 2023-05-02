from storage.fetch import find_candles
from enums.entity import Entity
from storage.db import db


def search_signal(code, klt=101):
    session = db.get_session(Entity.Single)
    candles = find_candles(code, klt)


def is_balance(diff):
    pass


if __name__ == '__main__':
    pass

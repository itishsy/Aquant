from dataclasses import dataclass
from sqlalchemy import select, desc, and_, text
from storage.dba import db
from typing import List
from datetime import datetime, timedelta


@dataclass
class Symbol:
    def __init__(self, series=None):
        if series is not None:
            for key in series.keys():
                setattr(self, key, series[key])

    id: int
    code: str
    name: str
    status: int
    comment: str



def find_active_symbols() -> List[Symbol]:
    session = db.get_session()
    sbs = session.execute(
        select(Symbol).where(and_(Symbol.status == 1))
    ).scalars().fetchall()
    session.close()
    return sbs


def update_all_symbols(status=0, beyond=None):
    session = db.get_session()
    try:
        update_sql = "UPDATE `symbol` SET `status` = {}".format(status)
        if status == 1:
            update_sql = "{} WHERE `code` LIKE '60%' OR `code` LIKE '30%' OR `code` LIKE '00%'".format(update_sql)
        session.execute(text(update_sql))
        # session.commit()
        if beyond is not None:
            b_status = 1 if status == 0 else 0
            update_sql2 = "UPDATE `symbol` SET `status` = {} WHERE `code` IN ({})".format(b_status, beyond)
            session.execute(text(update_sql2))
        session.flush()
        session.commit()
    except:
        session.rollback()


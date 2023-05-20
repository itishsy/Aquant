from sqlalchemy.orm import sessionmaker, registry
import config as cfg
from storage.mapping import do_mapping
from entities.candle import Candle
from entities.signal import Signal
from entities.symbol import Symbol
from entities.ticket import Ticket
from sqlalchemy import select, desc, and_, text
from typing import List
from datetime import datetime, timedelta
from enums.entity import Entity
from sqlalchemy import (
    create_engine,
    MetaData
)


class DB:
    meta = MetaData()

    def get_engine(self, code=''):
        dbname = 'aq'
        if code[0:2] in cfg.prefix:
            dbname = 'aq_{}'.format(code[0:2])
        engine = create_engine(
            'mysql+pymysql://{0}:{1}@{2}:{3}/{4}'.format(
                cfg.username,
                cfg.password,
                cfg.host,
                cfg.port,
                dbname),
            # 超过链接池大小外最多创建的链接
            max_overflow=0,
            # 链接池大小
            pool_size=5,
            # 链接池中没有可用链接则最多等待的秒数，超过该秒数后报错
            pool_timeout=10,
            # 多久之后对链接池中的链接进行一次回收
            pool_recycle=1,
            # 查看原生语句（未格式化）
            echo=False)
        return engine

    def get_session(self, table_name=''):
        engine = self.get_engine(table_name)
        for key in self.meta.tables.keys():
            if key[0:2] in cfg.prefix:
                if key != table_name:
                    self.meta.remove(self.meta.tables.get(key))
                    break
        do_mapping(engine, self.meta, table_name)
        return sessionmaker(bind=engine)()


db = DB()

kls = [102, 101, 60, 30, 15]


def find_active_symbols() -> List[Symbol]:
    session = db.get_session(Entity.Symbol)
    sbs = session.execute(
        select(Symbol).where(and_(Symbol.status == 1))
    ).scalars().fetchall()
    return sbs


def update_all_symbols(status=0, beyond=None):
    session = db.get_session(Entity.Symbol)
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


def find_candles(code, klt, begin='2015-01-01', end=None, limit=10000) -> List[Candle]:
    session = db.get_session(code)
    clauses = and_(Candle.klt == klt, Candle.dt >= begin)
    if end is not None:
        clauses = clauses.__and__(Candle.dt < end)
    cds = session.execute(
        select(Candle).where(clauses).order_by(desc(Candle.dt)).limit(limit)
    ).scalars().fetchall()
    return list(reversed(cds))


def find_stage_candles(code, klt, candle) -> List[Candle]:
    """
    根据一根candle查找所处指定级别的一段candles
    :param code:
    :param klt:
    :param candle:
    :return:
    """
    if klt == candle.klt:
        dt = candle.dt
    else:
        if candle.klt > 100:
            beg = datetime.strptime(candle.dt, '%Y-%m-%d')
        else:
            beg = datetime.strptime(candle.dt, '%Y-%m-%d %H:%M')
        if klt > 100:
            dt = beg.strftime('%Y-%m-%d')
        else:
            dt = beg.strftime('%Y-%m-%d %H:%M')

    session = db.get_session(code)
    clauses = and_(Candle.klt == klt, Candle.dt <= dt)
    cds = []
    pre_candles = session.execute(
        select(Candle).where(clauses).order_by(desc(Candle.dt)).limit(100)
    ).scalars().fetchall()
    for pc in pre_candles:
        if (pc.mark > 0) == (candle.mark > 0):
            cds.insert(0, pc)
        else:
            break
    clauses = and_(Candle.klt == klt, Candle.dt > dt)
    nex_candles = session.execute(
        select(Candle).where(clauses).order_by(Candle.dt).limit(100)
    ).scalars().fetchall()
    for nc in nex_candles:
        if (nc.mark > 0) == (candle.mark > 0):
            cds.append(nc)
        else:
            break
    return cds


def find_signals(notify=0, begin=None) -> List[Signal]:
    session = db.get_session(Entity.Signal)
    clauses = and_(Signal.notify == notify)
    if begin is not None:
        clauses = clauses.__and__(Signal.created > begin)
    sgs = session.execute(
        select(Signal).where(clauses)
    ).scalars().fetchall()
    return sgs


def find_tickets() -> List[Ticket]:
    session = db.get_session('ticket')
    clauses = and_(Ticket.status == 1)
    tis = session.execute(
        select(Ticket).where(clauses)
    ).scalars().fetchall()
    return tis


def update_signal_notify(signals: List[Signal]):
    session = db.get_session(Entity.Signal)
    mappings = []
    for s in signals:
        dic = {'id': s.id, 'notify': 1}
        mappings.append(dic)
    session.bulk_update_mappings(Signal, mappings)
    session.flush()
    session.commit()


def update_ticket(mappings):
    session = db.get_session(Entity.Ticket)
    session.bulk_update_mappings(Ticket, mappings)
    session.flush()
    session.commit()


if __name__ == '__main__':
    # fetch_symbols()
    # mark('300223', 101)
    # fetch_data('300223', 30)
    # candles = find_candles('300223', 101, begin='2023-01-01', limit=100)
    # for c in candles:
    #     print(c)
    fas = find_active_symbols()
    for sb in fas:
        print(sb.code)

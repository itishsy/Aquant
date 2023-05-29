from sqlalchemy.orm import sessionmaker, registry
from conf.config import Config
from storage.mapping import do_mapping
from entities.candle import Candle
from entities.signal import Signal
from entities.symbol import Symbol
from entities.ticket import Ticket
from sqlalchemy import select, desc, and_, text
from typing import List
from datetime import datetime, timedelta
from enums.entity import Entity
from sqlalchemy import create_engine, MetaData
import traceback


class DB:
    meta = MetaData()

    def get_engine(self, code=''):
        dbname = Config.DB_DATABASE
        if code[0:2] in Config.PREFIX:
            dbname = 'aq_{}'.format(code[0:2])
        engine = create_engine(
            'mysql+pymysql://{0}:{1}@{2}:{3}/{4}'.format(
                Config.DB_USER,
                Config.DB_PASSWD,
                Config.DB_HOST,
                Config.DB_PORT,
                dbname),
            # 超过链接池大小外最多创建的链接
            max_overflow=100,
            # 链接池大小
            pool_size=100,
            # 链接池中没有可用链接则最多等待的秒数，超过该秒数后报错
            pool_timeout=20,
            # 多久之后对链接池中的链接进行一次回收
            pool_recycle=10,
            # 查看原生语句（未格式化）
            echo=True)
        return engine

    def get_session(self, table_name=''):
        engine = self.get_engine(table_name)
        for key in self.meta.tables.keys():
            if key[0:2] in Config.PREFIX:
                if key != table_name:
                    self.meta.remove(self.meta.tables.get(key))
                    break
        do_mapping(engine, self.meta, table_name)
        return sessionmaker(bind=engine)()


db = DB()

freqs = [102, 101, 60, 30]


def find_active_symbols() -> List[Symbol]:
    session = db.get_session(Entity.Symbol)
    sbs = session.execute(
        select(Symbol).where(and_(Symbol.status == 1))
    ).scalars().fetchall()
    session.close()
    return sbs


def update_all_symbols(status=0, beyond=None):
    session = db.get_session(Entity.Symbol)
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


def find_candles(code, freq, begin='2015-01-01', end=None, limit=10000) -> List[Candle]:
    if begin is None:
        begin = '2015-01-01'
    session = db.get_session(code)
    clauses = and_(Candle.freq == freq, Candle.dt >= begin)
    if end is not None:
        clauses = clauses.__and__(Candle.dt < end)
    cds = session.execute(
        select(Candle).where(clauses).order_by(desc(Candle.dt)).limit(limit)
    ).scalars().fetchall()
    session.close()
    return list(reversed(cds))


def find_stage_candles(code, freq, candle) -> List[Candle]:
    """
    根据一根candle查找所处指定级别的一段candles
    :param code:
    :param freq:
    :param candle:
    :return:
    """
    if freq == candle.freq:
        dt = candle.dt
    else:
        if candle.freq > 100:
            beg = datetime.strptime(candle.dt, '%Y-%m-%d')
        else:
            beg = datetime.strptime(candle.dt, '%Y-%m-%d %H:%M')
        if freq > 100:
            dt = beg.strftime('%Y-%m-%d')
        else:
            dt = beg.strftime('%Y-%m-%d %H:%M')

    session = db.get_session(code)
    clauses = and_(Candle.freq == freq, Candle.dt <= dt)
    cds = []
    pre_candles = session.execute(
        select(Candle).where(clauses).order_by(desc(Candle.dt)).limit(100)
    ).scalars().fetchall()
    for pc in pre_candles:
        if (pc.mark > 0) == (candle.mark > 0):
            cds.insert(0, pc)
        else:
            break
    clauses = and_(Candle.freq == freq, Candle.dt > dt)
    nex_candles = session.execute(
        select(Candle).where(clauses).order_by(Candle.dt).limit(100)
    ).scalars().fetchall()
    for nc in nex_candles:
        if (nc.mark > 0) == (candle.mark > 0):
            cds.append(nc)
        else:
            break
    session.close()
    return cds


def find_signals(watch=None) -> List[Signal]:
    session = db.get_session(Entity.Signal)
    if watch is None:
        clauses = and_(1 == 1)
    else:
        clauses = and_(Signal.watch == watch)
    sgs = session.execute(
        select(Signal).where(clauses)
    ).scalars().fetchall()
    session.close()
    return sgs


def get_signal(id) -> Signal:
    session = db.get_session(Entity.Signal)
    sig = session.execute(
        select(Signal).where(Signal.id == id)
    ).scalar()
    session.close()
    return sig


def count_signals(today=False):
    session = db.get_session(Entity.Signal)
    if today:
        dt = datetime.now().strftime('%Y-%m-%d')
        count = session.query(Signal).filter(Signal.created >= dt).count()
    else:
        count = session.query(Signal).count()
    session.close()
    return count


def find_tickets() -> List[Ticket]:
    session = db.get_session('ticket')
    clauses = and_(Ticket.status == 1)
    tis = session.execute(
        select(Ticket).where(clauses)
    ).scalars().fetchall()
    session.close()
    return tis


def get_ticket(code) -> Signal:
    session = db.get_session(Entity.Ticket)
    sig = session.execute(
        select(Ticket).where(Ticket.code == code)
    ).scalar()
    session.close()
    return sig

def count_tickets():
    session = db.get_session(Entity.Ticket)
    count = session.query(Ticket).count()
    session.close()
    return count


def update_signal_watch(ident, watch):
    session = db.get_session(Entity.Signal)
    try:
        mappings = [{'id': ident, 'watch': watch}]
        session.bulk_update_mappings(Signal, mappings)
        session.flush()
        session.commit()
    except:
        session.rollback()


def save_ticket_by_signal(signal: Signal, status):
    session = db.get_session(Entity.Ticket)
    try:
        tic = get_ticket(signal.code)
        if tic is None:
            print('==========', signal)
            ticket = Ticket(signal.code,signal.dt,signal.freq)
            ticket.type = 0
            ticket.status = status
            ticket.created = datetime.now()
            ticket.updated = datetime.now()
            print('==========', ticket)
            session.add(ticket)
            session.commit()
        else:
            mappings = [{'id': tic.id, 'status': status}]
            session.bulk_update_mappings(Ticket, mappings)
            session.flush()
            session.commit()
        return 1
    except Exception as ex:
        traceback.print_exc()
        session.rollback()
        return 0

    def update_ticket(mappings):
        session = db.get_session(Entity.Ticket)
        try:
            session.bulk_update_mappings(Ticket, mappings)
            session.flush()
            session.commit()
        except:
            session.rollback()

    if __name__ == '__main__':
        pass
        # fetch_symbols()
        # mark('300223', 101)
        # fetch_data('300223', 30)
        # candles = find_candles('300223', 101, begin='2023-01-01', limit=100)
        # for c in candles:
        #     print(c)
        # fas = find_active_symbols()
        # for sb in fas:
        #     sql = "ALTER TABLE `{}` CHANGE `klt` `freq` INT(11) NULL;".format(sb.code)
        #     session = db.get_session(sb.code)
        #     session.execute(text(sql))
        #     session.flush()
        #     session.commit()

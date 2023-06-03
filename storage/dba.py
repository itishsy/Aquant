import efinance as ef
from sqlalchemy.orm import sessionmaker, registry
from conf.config import Config
from typing import List
from datetime import datetime, timedelta
from storage.candle import Candle
from storage.symbol import Symbol
from sqlalchemy import (
    create_engine,
    MetaData,
    select,
    desc,
    and_,
    Table,
    Column,
    Integer,
    String,
    DECIMAL,
    text
)


class DBA:
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
            echo=False)
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


dba = DBA()

freqs = [102, 101, 60, 30]


def fetch_symbols():
    session = dba.get_session()
    sbs = session.query(Symbol).all()
    if len(sbs) == 0:
        df = ef.stock.get_realtime_quotes(['沪A', '深A', 'ETF'])
        df = df.iloc[:, 0:2]
        df.columns = ['code', 'name']
        # df = df[df['name'].str.contains('ST') is False]
        symbols = []
        for i, row in df.iterrows():
            s = Symbol(row)
            s.status = 1
            symbols.append(s)
        session.add_all(symbols)
        session.commit()


def get_symbol(code):
    session = dba.get_session('symbol')
    sbs = session.query(Symbol).filter(Symbol.code==code).first()
    return sbs


def find_candles(code, freq, begin=None, end=None, limit=100) -> List[Candle]:
    session = dba.get_session(code)
    clauses = and_(Candle.freq == freq)
    if begin is not None:
        clauses = clauses.__and__(Candle.dt >= begin)
    if end is not None:
        clauses = clauses.__and__(Candle.dt < end)
    cds = session.execute(
        select(Candle).where(clauses).order_by(desc(Candle.dt)).limit(limit)
    ).scalars().fetchall()
    session.close()
    return list(reversed(cds))


def find_stage_candles(code, freq, candle) -> List[Candle]:
    """
    根据一根candle查找所处指定级别的一段candles,bar同向的一段
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

    session = dba.get_session(code)
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


def find_active_symbols() -> List[Symbol]:
    session = dba.get_session('symbol')
    sbs = session.execute(
        select(Symbol).where(and_(Symbol.status == 1))
    ).scalars().fetchall()
    session.close()
    return sbs


def update_all_symbols(status=0, beyond=None):
    session = dba.get_session('symbol')
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



class Mapper:
    reg = registry()

    def candle_table(self, meta, code):
        self.reg.dispose()
        self.reg.map_imperatively(Candle, Table(
            code, meta,
            Column('id', Integer, autoincrement=True, primary_key=True),
            Column('dt', String(50)),
            Column('freq', Integer),
            Column('open', DECIMAL(8, 2)),
            Column('close', DECIMAL(8, 2)),
            Column('high', DECIMAL(8, 2)),
            Column('low', DECIMAL(8, 2)),
            Column('volume', DECIMAL(12, 4), default=None),
            Column('turnover', DECIMAL(12, 4), default=None),
            Column('ma5', DECIMAL(12, 4), default=None),
            Column('ma10', DECIMAL(12, 4), default=None),
            Column('ma20', DECIMAL(12, 4), default=None),
            Column('ma30', DECIMAL(12, 4), default=None),
            Column('mav5', DECIMAL(12, 4), default=None),
            Column('ema12', DECIMAL(12, 4), default=None),
            Column('ema26', DECIMAL(12, 4), default=None),
            Column('dea9', DECIMAL(12, 4), default=None),
            Column('mark', Integer)
        ))

    def symbol_table(self, meta):
        registry().map_imperatively(Symbol, Table(
            'symbol', meta,
            Column('id', Integer, autoincrement=True, primary_key=True),
            Column('code', String(50)),
            Column('name', String(50)),
            Column('status', Integer),
            Column('comment', String(500))
        ))
    #
    # def signal_table(self, meta):
    #     registry().map_imperatively(Signal, Table(
    #         Entity.Signal, meta,
    #         Column('id', Integer, autoincrement=True, primary_key=True),
    #         Column('code', String(50)),
    #         Column('dt', String(50)),
    #         Column('freq', Integer),
    #         Column('type', String(50)),
    #         Column('value', String(50)),
    #         Column('watch', Integer),
    #         Column('notify', Integer),
    #         Column('created', DateTime)
    #     ))
    #
    # def ticket_table(self, meta):
    #     registry().map_imperatively(Ticket, Table(
    #         Entity.Ticket, meta,
    #         Column('id', Integer, autoincrement=True, primary_key=True),
    #         Column('code', String(50)),
    #         Column('type', String(50)),
    #         Column('freq', Integer),
    #         Column('dt', String(50)),
    #         Column('status', Integer),
    #         Column('created', DateTime),
    #         Column('updated', DateTime)
    #     ))


def do_mapping(engine, meta, table_name):
    if meta.tables.get(table_name) is None:
        mapper = Mapper()
        if table_name[0:2] in Config.PREFIX:
            mapper.candle_table(meta, table_name)
        else:
            eval('mapper.{}_table'.format(table_name))(meta)
        meta.tables.get(table_name).create(engine, checkfirst=True)


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

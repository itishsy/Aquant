from sqlalchemy.orm import sessionmaker, registry
import config as cfg
from entities.candle import Candle
from entities.signal import Signal
from enums.entity import Entity
from storage.mapping import mapping
from sqlalchemy import (
    create_engine,
    MetaData,
    Table,
    Column,
    Integer,
    String,
    DECIMAL
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
            echo=True)
        return engine

    def get_session(self, table_name=''):
        engine = self.get_engine(table_name)
        mapping(engine, self.meta, table_name)
        # if self.meta.tables.get(table_name) is None:
        #     if table_name[0:2] in cfg.prefix:
        #         candle_mapping(self.meta, table_name)
        #     else:
        #         print('----------', table_name)
        #         common_mapping(self.meta, table_name)
        #     self.meta.tables.get(table_name).create(engine, checkfirst=True)
        return sessionmaker(bind=engine)()


db = DB()


def candle_mapping(meta, code):
    registry().map_imperatively(Candle, Table(
        code, meta,
        Column('id', Integer, autoincrement=True, primary_key=True),
        Column('dt', String(50)),
        Column('klt', Integer),
        Column('open', DECIMAL(8, 2)),
        Column('close', DECIMAL(8, 2)),
        Column('high', DECIMAL(8, 2)),
        Column('low', DECIMAL(8, 2)),
        Column('volume', DECIMAL(12, 4), default=None),
        Column('turnover', DECIMAL(12, 4), default=None),
        Column('ma5', DECIMAL(12, 4), default=None),
        Column('ma10', DECIMAL(12, 4), default=None),
        Column('ma20', DECIMAL(12, 4), default=None),
        Column('ema12', DECIMAL(12, 4), default=None),
        Column('ema26', DECIMAL(12, 4), default=None),
        Column('dea9', DECIMAL(12, 4), default=None),
        Column('ma_mark', Integer),
        Column('macd_mark', Integer)
    ))


def common_mapping(meta, table_name):
    print('----', (table_name == Entity.Single))
    if table_name == Entity.Single:
        registry().map_imperatively(Signal, Table(
            table_name, meta,
            Column('id', Integer, autoincrement=True, primary_key=True),
            Column('code', String(50)),
            Column('dt', String(50)),
            Column('klt', Integer),
            Column('type', String(50))
        ))

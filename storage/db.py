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
        return sessionmaker(bind=engine)()


db = DB()

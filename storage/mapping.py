from sqlalchemy.orm import registry
from entities.candle import Candle
from entities.signal import Signal
from enums.entity import Entity
import config as cfg
from sqlalchemy import (
    Table,
    Column,
    Integer,
    String,
    DECIMAL
)


class Mapper:
    def candle_table(self, meta, code):
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

    def single_table(self, meta):
        registry().map_imperatively(Signal, Table(
            Entity.Single, meta,
            Column('id', Integer, autoincrement=True, primary_key=True),
            Column('code', String(50)),
            Column('dt', String(50)),
            Column('klt', Integer),
            Column('type', String(50)),
            Column('value', String(50))
        ))


def mapping(engine, meta, table_name):
    if meta.tables.get(table_name) is None:
        mapper = Mapper()
        if table_name[0:2] in cfg.prefix:
            mapper.candle_table(meta, table_name)
        else:
            eval('mapper.{}_table'.format(table_name))(meta)
        meta.tables.get(table_name).create(engine, checkfirst=True)

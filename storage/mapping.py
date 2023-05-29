from sqlalchemy.orm import registry
from entities.candle import Candle
from entities.signal import Signal
from entities.symbol import Symbol
from entities.ticket import Ticket
from enums.entity import Entity
from conf.config import Config
from sqlalchemy import (
    Table,
    Column,
    Integer,
    String,
    DECIMAL,
    DateTime
)


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
            Entity.Symbol, meta,
            Column('id', Integer, autoincrement=True, primary_key=True),
            Column('code', String(50)),
            Column('name', String(50)),
            Column('status', Integer),
            Column('comment', String(500))
        ))

    def signal_table(self, meta):
        registry().map_imperatively(Signal, Table(
            Entity.Signal, meta,
            Column('id', Integer, autoincrement=True, primary_key=True),
            Column('code', String(50)),
            Column('dt', String(50)),
            Column('freq', Integer),
            Column('type', String(50)),
            Column('value', String(50)),
            Column('watch', Integer),
            Column('notify', Integer),
            Column('created', DateTime)
        ))

    def ticket_table(self, meta):
        registry().map_imperatively(Ticket, Table(
            Entity.Ticket, meta,
            Column('id', Integer, autoincrement=True, primary_key=True),
            Column('code', String(50)),
            Column('type', String(50)),
            Column('freq', Integer),
            Column('dt', String(50)),
            Column('status', Integer),
            Column('created', DateTime),
            Column('updated', DateTime)
        ))


def do_mapping(engine, meta, table_name):
    if meta.tables.get(table_name) is None:
        mapper = Mapper()
        if table_name[0:2] in Config.PREFIX:
            mapper.candle_table(meta, table_name)
        else:
            eval('mapper.{}_table'.format(table_name))(meta)
        meta.tables.get(table_name).create(engine, checkfirst=True)

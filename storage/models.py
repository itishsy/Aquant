import datetime
from sqlalchemy.orm import sessionmaker, mapper, registry
from dataclasses import dataclass, field
import config as cfg
from sqlalchemy import (
    create_engine,
    MetaData,
    Table,
    Column,
    Integer,
    String,
    Enum,
    DECIMAL,
    DateTime,
    Boolean,
    UniqueConstraint,
    Index,
    select
)


@dataclass
class Person:
    id: int = None
    name: str = field(default_factory=str)


if __name__ == "__main__":
    table_name = '000001'

    # 创建引擎
    engine = create_engine(
        "mysql+pymysql://{0}:{1}@{2}:{3}/{4}".format(
            cfg.username,
            cfg.password,
            cfg.host,
            cfg.port,
            "agu"),
        # 超过链接池大小外最多创建的链接
        max_overflow=0,
        # 链接池大小
        pool_size=5,
        # 链接池中没有可用链接则最多等待的秒数，超过该秒数后报错
        pool_timeout=10,
        # 多久之后对链接池中的链接进行一次回收
        pool_recycle=1,
        # 查看原生语句（未格式化）
        echo=True
    )

    meta = MetaData()

    table = Table(
        table_name, meta,
        Column('id', Integer, primary_key=True),
        Column('name', String(50))
    )
    registry().map_imperatively(Person, table)
    meta.create_all(engine)

    session = sessionmaker(bind=engine)()

    person = Person(name='bot')
    session.add(person)
    session.commit()

    result = session.execute(select(Person))
    for r in result.scalars():
        print(r.name)
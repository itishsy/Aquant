from sqlalchemy.orm import sessionmaker, registry
from conf.config import Config
from storage.mapping import do_mapping
from sqlalchemy import create_engine, MetaData


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

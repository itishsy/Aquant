from models.base import BaseModel, db
from flask_peewee.db import CharField, IntegerField, DateTimeField


class Engine(BaseModel):
    name = CharField()  # 名称
    method = CharField()  # 方法
    job_from = IntegerField(default=0)  # 作业开始
    job_to = IntegerField(default=0)  # 作业截止
    job_times = IntegerField(default=0)  # 执行次数，0不限制
    run_start = DateTimeField()  # 最近执行时间
    run_end = DateTimeField()  # 最近执行时间
    status = IntegerField(default=0)  # 状态 -1 禁用，0 待执行 1 执行中 2 执行结束
    comment = CharField()

    class Status:
        STOP = -1  # 禁用
        READY = 0  # 就绪
        RUNNING = 1  # 运行中
        DONE = 2  # 完成

    @staticmethod
    def init():
        Engine.create(name='fetcher', method='symbols', job_from='1600', job_to='2300', job_times=5, status=0)
        Engine.create(name='fetcher', method='candles', job_from='1600', job_to='2300', job_times=1, status=0)
        Engine.create(name='searcher', method='u20', job_from='1600', job_to='2300', job_times=1, status=0)
        Engine.create(name='searcher', method='u60', job_from='1600', job_to='2300', job_times=1, status=0)
        Engine.create(name='searcher', method='u10', job_from='1600', job_to='2300', job_times=1, status=0)
        Engine.create(name='watcher', method='b5', job_from='930', job_to='1500', job_times=0, status=0)
        Engine.create(name='watcher', method='b15', job_from='930', job_to='1500', job_times=0, status=0)


if __name__ == '__main__':
    db.connect()
    db.create_tables([Engine])

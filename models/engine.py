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
    status = IntegerField(default=0)  # 状态

    class Status:
        STOP = -1  # 停用
        READY = 0  # 就绪
        RUNNING = 1  # 运行中


if __name__ == '__main__':
    db.connect()
    db.create_tables([Engine])

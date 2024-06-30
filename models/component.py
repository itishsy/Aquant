from models.base import BaseModel, db
from flask_peewee.db import CharField, IntegerField, DateTimeField


class Component(BaseModel):
    name = CharField()  # 名称
    clock_time = DateTimeField()  # 最近打卡时间
    run_start = DateTimeField()  # 最近执行时间
    run_end = DateTimeField()  # 最近执行时间
    status = IntegerField(default=0)  # 状态

    class Status:
        STOP = 0  # 停用
        READY = 1  # 就绪
        RUNNING = 2  # 运行中


if __name__ == '__main__':
    db.connect()
    db.create_tables([Component])

from models.base import BaseModel
from flask_peewee.db import CharField, IntegerField, DateTimeField


# 通知
class Component(BaseModel):
    name = CharField()  # 名称
    clock_time = DateTimeField()  # 最近打卡时间
    run_start = DateTimeField()  # 最近执行时间
    run_end = DateTimeField()  # 最近执行时间
    frequency = IntegerField()  # 执行频率（分钟）
    status = IntegerField(default=0)  # 状态


class COMPONENT_TYPE:
    FETCHER = 'fetcher'
    SENDER = 'sender'
    SEARCHER = '{0}_searcher'
    WATCHER = '{0}_watcher'


class COMPONENT_STATUS:
    STOP = '停用'
    READY = '就绪'
    RUNNING = '运行中'


def start_watch(comp):
    return False


def done_watch(comp):
    pass

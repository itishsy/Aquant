# -*- coding: utf-8 -*-

from peewee import MySQLDatabase, Model, CharField, BooleanField, IntegerField, DateTimeField
import json
from werkzeug.security import check_password_hash
from flask_login import UserMixin
from app import login_manager
from conf.config import config
import os

cfg = config[os.getenv('FLASK_CONFIG') or 'default']

db = MySQLDatabase(host=cfg.DB_HOST, user=cfg.DB_USER, passwd=cfg.DB_PASSWD, database=cfg.DB_DATABASE)


class BaseModel(Model):
    class Meta:
        database = db

    def __str__(self):
        r = {}
        for k in self._data.keys():
            try:
                r[k] = str(getattr(self, k))
            except:
                r[k] = json.dumps(getattr(self, k))
        # return str(r)
        return json.dumps(r, ensure_ascii=False)


# 用户
class User(UserMixin, BaseModel):
    username = CharField()  # 用户名
    password = CharField()  # 密码
    fullname = CharField()  # 真实性名
    email = CharField()  # 邮箱
    phone = CharField()  # 电话
    status = BooleanField(default=True)  # 生效失效标识

    def verify_password(self, raw_password):
        return check_password_hash(self.password, raw_password)


# 通知
class Notify(BaseModel):
    code = CharField() # 编码
    strategy = CharField()  # 策略
    dt = CharField()  # 发生时间
    status = IntegerField(default=0)  # 0 未发送 1 已发送
    created = DateTimeField()
    updated = DateTimeField()


# 信号
class Signal(BaseModel):
    code = CharField()  # 编码
    dt = CharField()  # 时间
    freq = CharField()  # 周期
    strategy = CharField()  # 策略类型
    value = CharField()  # 策略值
    tick = BooleanField(default=True)  # 是否票据
    created = DateTimeField


# 票据
class Ticket(BaseModel):
    code = CharField()  # 编码
    dt = CharField()  # 时间
    freq = CharField()  # 周期
    strategy = CharField()  # 策略类型
    status = BooleanField(default=True) # 状态


@login_manager.user_loader
def load_user(user_id):
    return User.get(User.id == int(user_id))


# 建表
def create_table():
    db.connect()
    db.create_tables([Notify, User, Signal, Ticket])


if __name__ == '__main__':
    create_table()

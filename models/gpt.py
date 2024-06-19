from models.base import BaseModel, db
from flask_peewee.db import CharField, AutoField, DateTimeField, IntegerField


# 通知
class Gpt(BaseModel):
    id = AutoField()
    model = CharField()  # 名称
    message = CharField(max_length=500)  # 名称
    content = CharField(max_length=5000)  # 名称
    status = IntegerField(default=1)  # 状态
    created = DateTimeField()


if __name__ == '__main__':
    db.connect()
    db.create_tables([Gpt])

from models.base import BaseModel
from flask_peewee.db import CharField, IntegerField
from datetime import datetime


# HOT
class Hot(BaseModel):
    code = CharField()  # 票据
    name = CharField()  # 名称
    source = CharField()  # 来源
    rank = IntegerField()  # 排名
    created = CharField()

    @staticmethod
    def add(cod, nam, sou, ran):
        cre = datetime.now().strftime("%Y-%m-%d")
        if not Hot.select().where(Hot.code == cod, Hot.source == sou, Hot.created == cre).exists():
            hot = Hot()
            hot.code = cod
            hot.name = nam
            hot.source = sou
            hot.rank = ran
            hot.created = cre
            hot.save()

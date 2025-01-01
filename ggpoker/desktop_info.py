from models.base import BaseModel, db
from flask_peewee.db import CharField, IntegerField, DateTimeField, AutoField, DecimalField


# 入选池
class DesktopInfo(BaseModel):
    id = AutoField()
    game = CharField()  # 牌局
    round = IntegerField()  # 回合
    card1 = CharField()  # 手牌1
    card2 = CharField()  # 手牌1
    card3 = CharField()  # 公共牌1
    card4 = CharField()  # 公共牌2
    card5 = CharField()  # 公共牌3
    card6 = CharField()  # 公共牌4
    card7 = CharField()  # 公共牌5
    pool = DecimalField()  # 底池
    created = DateTimeField()

    def to_string(self):
        return "手牌: {}、{} 公共牌: {}、{}、{}、{},{} 底池: {}".format(self.card1, self.card2,
                                                             self.card3, self.card4, self.card5, self.card6, self.card7,
                                                             self.pool)

    def equals(self, desktop_info):
        return self.to_string() == desktop_info.to_string()


if __name__ == '__main__':
    db.connect()
    db.create_tables([DesktopInfo])

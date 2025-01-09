from models.base import BaseModel, db
from flask_peewee.db import CharField, IntegerField, DateTimeField, AutoField, DecimalField


# 牌局信息。每发一次牌为新的牌局
class Game(BaseModel):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.sections = []

    id = AutoField()
    code = CharField()  # 牌局
    card1 = CharField()  # 手牌1
    card2 = CharField()  # 手牌1
    seat = IntegerField()  # 座位
    created = DateTimeField()

    stage = CharField()  # 阶段
    sections = []

    def get_info(self):
        return 'ID: {} 手牌: {}|{} 位置: {}'.format(self.code, self.card1, self.card2, self.seat)



# 牌桌信息
class Section(BaseModel):
    id = AutoField()
    pool = DecimalField()  # 底池
    seat = IntegerField()  # 座位
    card1 = CharField()  # 公共牌1
    card2 = CharField()  # 公共牌2
    card3 = CharField()  # 公共牌1
    card4 = CharField()  # 公共牌2
    card5 = CharField()  # 公共牌3
    card6 = CharField()  # 公共牌4
    card7 = CharField()  # 公共牌5
    action = CharField()  # 操作
    created = DateTimeField()

    player1 = CharField()   # 玩家1
    player1_amount = DecimalField()  #
    player1_action = CharField()  #
    player2 = CharField()   # 玩家2
    player2_amount = DecimalField()  #
    player2_action = CharField()  #
    player3 = CharField()   # 玩家3
    player3_amount = DecimalField()  #
    player3_action = CharField()  #
    player4 = CharField()   # 玩家4
    player4_amount = DecimalField()  #
    player4_action = CharField()  #
    player5 = CharField()   # 玩家5
    player5_amount = DecimalField()  #
    player5_action = CharField()  #

    def to_string(self):
        return ("手牌:{}|{}, 位置:{}, 底池:{}, 公共牌: {}|{}|{}|{}|{}, 玩家: {}|{}|{}|{}|{}"
                .format(self.card1, self.card2, self.seat, self.pool,
                        self.card3, self.card4, self.card5, self.card6, self.card7,
                        self.player1, self.player2, self.player3, self.player4, self.player5))

    def equals(self, sec):
        return (self.pool == sec.pool and self.card3 == sec.card3 and self.card4 == sec.card4
                and self.card5 == sec.card5 and self.card6 == sec.card6 and self.card7 == sec.card7
                and self.seat == sec.seat)

    def get_stage(self):
        if not self.card3:
            return 'PreFlop'
        elif not self.card6:
            return 'Flop'
        elif not self.card7:
            return 'Turn'
        return 'River'


class Player(BaseModel):
    id = AutoField()
    name = CharField()
    seat = CharField()
    balance = DecimalField()  # 余额


class Stage:
    PreFlop = 1
    Flop = 2
    Turn = 3
    River = 4


class Action:
    Null = 'NG'
    Fold = 'Fold'
    Check = 'Check'
    Call = 'Call'
    Raise = 'Raise'
    AllIn = 'AllIn'


if __name__ == '__main__':
    pass
    # db.connect()
    # db.create_tables([DesktopInfo])

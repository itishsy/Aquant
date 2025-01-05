from models.base import BaseModel, db
from flask_peewee.db import CharField, IntegerField, DateTimeField, AutoField, DecimalField
from datetime import datetime


# 牌局信息。每发一次牌为新的牌局
class Game(BaseModel):
    id = AutoField()
    code = CharField()  # 牌局
    card1 = CharField()  # 手牌1
    card2 = CharField()  # 手牌1
    seat = IntegerField()  # 座位
    created = DateTimeField()

    sections = []

    @staticmethod
    def new(card1, card2, seat):
        game = Game()
        game.code = datetime.now().strftime('%Y%m%d%H%M%S')
        game.card1 = card1
        game.card2 = card2
        game.seat = seat
        game.created = datetime.now()
        return game

    def load(self, section):
        self.sections.append(section)

    def print(self):
        print('ID:{}'.format(self.code))
        print('手牌:{}|{},位置:{}'.format(self.card1, self.card2, self.seat))
        size = len(self.sections)
        for i in range(size):
            sec = self.sections[i]
            print("【round{}】：底池:{}, 公共牌: {}|{}|{}|{}|{}, 玩家: {}|{}|{}|{}|{}".format(i, sec.pool, sec.card3, sec.card4, sec.card5, sec.card6, sec.card7,
                            sec.player1, sec.player2, sec.player3, sec.player4, sec.player5))


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
    created = DateTimeField()

    player1 = CharField()   # 玩家1
    player2 = CharField()   # 玩家2
    player3 = CharField()   # 玩家3
    player4 = CharField()   # 玩家4
    player5 = CharField()   # 玩家5

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
            return Stage.PreFlop
        elif not self.card6:
            return Stage.Flop
        elif not self.card7:
            return Stage.Turn
        return Stage.River

    def add_player(self, idx, player):
        if idx == 1:
            self.player1 = player
        elif idx == 2:
            self.player2 = player
        elif idx == 3:
            self.player3 = player
        elif idx == 4:
            self.player4 = player
        elif idx == 5:
            self.player5 = player


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
    Fold = -1
    Check = 0
    Call = 1
    Raise = 10
    AllIn = 100

    def to_string(self):
        if self == Action.Fold:
            return 'Fold'
        elif self == Action.Check:
            return 'Check'
        elif self == Action.Call:
            return 'Call'
        elif self == Action.Raise:
            return 'Raise'
        elif self == Action.AllIn:
            return 'AllIn'


if __name__ == '__main__':
    pass
    # db.connect()
    # db.create_tables([DesktopInfo])

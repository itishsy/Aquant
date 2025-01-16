from models.base import BaseModel, db
from flask_peewee.db import CharField, IntegerField, DateTimeField, AutoField, DecimalField
from datetime import datetime
from poker.player import Player, PlayerAction
from config import SB, BB
from decimal import Decimal


# 牌局信息。每发一次牌为新的牌局
class Game(BaseModel):

    id = AutoField()
    code = CharField()  # 牌局
    card1 = CharField()  # 手牌1
    card2 = CharField()  # 手牌2
    card3 = CharField()  # 公共牌1
    card4 = CharField()  # 公共牌2
    card5 = CharField()  # 公共牌3
    card6 = CharField()  # 公共牌4
    card7 = CharField()  # 公共牌5
    seat = IntegerField()  # 座位
    stage = CharField()  # 最终阶段
    created = DateTimeField()

    players = []
    sections = []
    actions = []

    @staticmethod
    def create_by_section(sec):
        game = Game()
        game.code = datetime.now().strftime('%Y%m%d%H%M%S')
        game.card1 = sec.card1
        game.card2 = sec.card2
        game.seat = sec.seat
        game.stage = 'PreFlop'
        game.created = datetime.now()
        game.sections = [sec]
        for i in range(1, 6):
            player_name = eval('sec.player{}'.format(i))
            player = Player()
            player.game_code = game.code
            player.seat = (sec.seat + i) % 6
            if player.seat == 0:
                player.seat = 6
            if player_name:
                player.name = player_name
                player.amount = eval('sec.player{}_amount'.format(i))
                player.status = 'playing' if player.amount else 'leave'
                act = PlayerAction()
                act.stage = 'PreFlop'
                act.round = 1
                act.amount = player.amount
                if player.seat == 1:
                    act.action = 'bet:{}'.format(SB)
                elif player.seat == 2:
                    act.action = 'bet:{}'.format(BB)
                elif player.seat < sec.seat and sec.pool == Decimal(str(SB+BB)):
                    act.action = 'fold'
                else:
                    act.action = 'pending'
                player.actions = [act]
            else:
                player.status = 'nobody'
            game.players.append(player)
        return game

    def append_section(self, section):
        self.card3 = section.card3
        self.card4 = section.card4
        self.card5 = section.card5
        self.card6 = section.card6
        self.card7 = section.card7
        pre_section = self.sections[-1]
        for i in range(5):
            player = self.players[i]
            if not player.actions:
                continue
            pre_action = player.actions[-1]
            player_name = eval('section.player{}'.format(i+1))
            if player_name:
                amount = eval('section.player{}_amount'.format(i+1))
                if amount:
                    player.status = 'playing'
                    act = PlayerAction()
                    act.stage = section.get_stage()
                    act.round = 1 if pre_action.stage != act.stage else pre_action.round + 1
                    act.amount = amount
                    if pre_action.amount > amount:
                        act.action = 'bet:{}'.format(pre_action.amount - amount)
                    elif pre_action.amount < amount:
                        act.action = 'fold'
                    else:
                        if pre_section.pool == section.pool:
                            act.action = 'check'
                        else:
                            if player.seat < section.seat:
                                act.action = 'fold'
                            else:
                                act.action = 'pending'
                    player.actions.append(act)
                else:
                    player.status = 'new'
            else:
                player.status = 'leave'
        self.sections.append(section)

    def get_action(self):
        if self.actions:
            return self.actions[-1]

    def get_info(self):
        return '位置: {} 手牌: {}|{}'.format(
            self.seat, self.card1, self.card2)


# 牌桌信息
class Section(BaseModel):
    """
    每次需要做决策时，根据捕获的tableImage生成一个section
    """
    id = AutoField()
    pool = DecimalField()  # 底池
    seat = IntegerField()  # 座位
    stage = CharField()  # 阶段
    card1 = CharField()  # 手牌1
    card2 = CharField()  # 手牌2
    card3 = CharField()  # 公共牌1
    card4 = CharField()  # 公共牌2
    card5 = CharField()  # 公共牌3
    card6 = CharField()  # 公共牌4
    card7 = CharField()  # 公共牌5
    action = CharField()  # 操作
    created = DateTimeField()

    player1 = CharField()   # 玩家1
    player1_amount = DecimalField()  #
    player2 = CharField()   # 玩家2
    player2_amount = DecimalField()  #
    player3 = CharField()   # 玩家3
    player3_amount = DecimalField()  #
    player4 = CharField()   # 玩家4
    player4_amount = DecimalField()  #
    player5 = CharField()   # 玩家5
    player5_amount = DecimalField()  #

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

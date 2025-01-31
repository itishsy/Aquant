from models.base import BaseModel, db
from flask_peewee.db import CharField, IntegerField, DateTimeField, AutoField, DecimalField
from datetime import datetime
from poker.player import Player, PlayerAction
from poker.config import SB, BB
from decimal import Decimal


# 牌局信息。每发一次牌为新的牌局
class Game(BaseModel):

    def __init__(self, section, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.code = datetime.now().strftime('%Y%m%d%H%M%S')
        self.card1 = section.card1
        self.card2 = section.card2
        self.seat = section.seat
        self.stage = section.stage
        self.created = datetime.now()
        self.players.clear()

        section.game_code = self.code
        for i in range(1, 6):
            player_name = eval('section.player{}_name'.format(i))
            amount = eval('section.player{}_amount'.format(i))
            if player_name and amount:
                seat = (section.seat + i) % 6
                seat = 6 if seat == 0 else seat
                exec('section.player{}_seat={}'.format(i, seat))
                if seat == 1:
                    exec("section.player{}_action='{}'".format(i, 'bet:{}'.format(SB)))
                elif seat == 2:
                    exec("section.player{}_action='{}'".format(i, 'bet:{}'.format(BB)))
                elif seat < section.seat and section.pool == Decimal(str(SB + BB)):
                    exec("section.player{}_action='{}'".format(i, 'fold'))
                else:
                    exec("section.player{}_action='{}'".format(i, 'pending'))
        self.sections = [section]

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

    action = None

    # @staticmethod
    # def create_by_section(section):
    # game = Game()
    # game.code = datetime.now().strftime('%Y%m%d%H%M%S')
    # game.card1 = section.card1
    # game.card2 = section.card2
    # game.seat = section.seat
    # game.stage = section.stage
    # game.created = datetime.now()
    # game.players.clear()
    #
    # section.game_code = game.code
    # for i in range(1, 6):
    #     player_name = eval('section.player{}_name'.format(i))
    #     amount = eval('section.player{}_amount'.format(i))
    #     # player = Player()
    #     if player_name and amount:
    #         seat = (section.seat + i) % 6
    #         seat = 6 if seat == 0 else seat
    #         exec('section.player{}_seat={}'.format(i, seat))
    #         # player.name = player_name
    #         # player.amount = eval('sec.player{}_amount'.format(i))
    #         # player.status = 'playing' if player.amount else 'leave'
    #         # act = PlayerAction()
    #         # act.stage = 'PreFlop'
    #         # act.round = 1
    #         # act.amount = player.amount
    #         if seat == 1:
    #             exec("section.player{}_action='{}'".format(i, 'bet:{}'.format(SB)))
    #         elif seat == 2:
    #             exec("section.player{}_action='{}'".format(i, 'bet:{}'.format(BB)))
    #             # act.action = 'bet:{}'.format(BB)
    #         elif seat < section.seat and section.pool == Decimal(str(SB+BB)):
    #             exec("section.player{}_action='{}'".format(i, 'fold'))
    #         else:
    #             exec("section.player{}_action='{}'".format(i, 'pending'))
    #         # player.actions = [act]
    #     # else:
    #     #     player.status = 'nobody'
    #     # game.players.append(player)
    # game.sections = [section]
    # return game

    def append_section(self, section):
        self.card3 = section.card3
        self.card4 = section.card4
        self.card5 = section.card5
        self.card6 = section.card6
        self.card7 = section.card7
        self.stage = section.stage

        section.game_code = self.code
        pre_section = self.sections[-1]
        for i in range(1, 6):
            # player = self.players[i]
            # if not player.actions:
            #     continue
            # pre_action = player.actions[-1]
            player_name = eval('section.player{}_name'.format(i))
            cur_amount = eval('section.player{}_amount'.format(i))
            pre_amount = eval('pre_section.player{}_amount'.format(i))
            pre_action = eval('pre_section.player{}_action'.format(i))
            if player_name and cur_amount:
                pre_seat = eval("pre_section.player{}_seat".format(i))
                exec("section.player{}_seat='{}'".format(i, pre_seat))
                if pre_amount > cur_amount:
                    exec("section.player{}_action='{}'".format(i, 'bet:{}'.format(pre_amount - cur_amount)))
                elif pre_amount < cur_amount:
                    exec("section.player{}_action='{}'".format(i, 'fold'))
                else:
                    if pre_section.pool < section.pool or pre_action == 'fold':
                        exec("section.player{}_action='{}'".format(i, 'fold'))
                    else:
                        exec("section.player{}_action='{}'".format(i, 'check'))

                    # player.status = 'playing'
                    # act = PlayerAction()
                    # act.stage = section.get_stage()
                    # act.round = 1 if pre_action.stage != act.stage else pre_action.round + 1
                    # act.amount = amount
                    # if pre_action.amount > amount:
                    #     act.action = 'bet:{}'.format(pre_action.amount - amount)
                    # elif pre_action.amount < amount:
                    #     act.action = 'fold'
                    # else:
                    #     if pre_section.pool == section.pool:
                    #         act.action = 'check'
                    #     else:
                    #         if player.seat < section.seat:
                    #             act.action = 'fold'
                    #         else:
                    #             act.action = 'pending'
                    # player.actions.append(act)
                # else:
                #     player.status = 'new'
            # else:
            #     player.status = 'leave'
        self.sections.append(section)

    def get_info(self):
        return '手牌: {},{} 位置: {}'.format(
            self.card1, self.card2, self.seat)


# 牌桌信息
class Section(BaseModel):
    """
    每次需要做决策时，根据捕获的tableImage生成一个section
    """
    id = AutoField()
    game_code = CharField()
    pool = DecimalField()  # 底池
    seat = IntegerField()  # 座位
    stage = CharField()  # 阶段
    card1 = CharField()  # 手牌1
    card2 = CharField()  # 手牌2
    card3 = CharField(null=True)  # 公共牌1
    card4 = CharField(null=True)  # 公共牌2
    card5 = CharField(null=True)  # 公共牌3
    card6 = CharField(null=True)  # 公共牌4
    card7 = CharField(null=True)  # 公共牌5
    action = CharField(null=True)  # 操作

    player1_name = CharField(null=True)  # 玩家1
    player1_amount = DecimalField(null=True)  #
    player1_seat = CharField(null=True)  #
    player1_action = CharField(null=True)  #
    player2_name = CharField(null=True)  # 玩家2
    player2_amount = DecimalField(null=True)  #
    player2_seat = CharField(null=True)  #
    player2_action = CharField(null=True)  #
    player3_name = CharField(null=True)  # 玩家3
    player3_amount = DecimalField(null=True)  #
    player3_seat = CharField(null=True)  #
    player3_action = CharField(null=True)  #
    player4_name = CharField(null=True)  # 玩家4
    player4_amount = DecimalField(null=True)  #
    player4_seat = CharField(null=True)  #
    player4_action = CharField(null=True)  #
    player5_name = CharField(null=True)  # 玩家5
    player5_amount = DecimalField(null=True)  #
    player5_seat = CharField(null=True)  #
    player5_action = CharField(null=True)  #

    def to_string(self):
        return ("手牌:{}|{}, 位置:{}, 底池:{}, 公共牌: {}|{}|{}|{}|{}, 玩家: {}|{}|{}|{}|{}"
                .format(self.card1, self.card2, self.seat, self.pool,
                        self.card3, self.card4, self.card5, self.card6, self.card7,
                        self.player1_name, self.player2_name, self.player3_name, self.player4_name, self.player5_name))

    def equals(self, sec):
        return (self.pool == sec.pool and self.card3 == sec.card3 and self.card4 == sec.card4
                and self.card5 == sec.card5 and self.card6 == sec.card6 and self.card7 == sec.card7
                and self.seat == sec.seat)

    def enabled(self):
        return self.card1 and self.card2 and self.pool and self.seat


if __name__ == '__main__':
    db.connect()
    db.create_tables([Section])

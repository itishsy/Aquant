from models.base import BaseModel, db
from flask_peewee.db import CharField, IntegerField, DateTimeField, AutoField, DecimalField


class Player(BaseModel):
    id = AutoField()
    game_code = CharField()
    name = CharField()
    seat = CharField()
    status = CharField()
    amount = DecimalField()  # 起始金额
    actions = []

    def eval_player_actions(self, sections, idx):
        s_len = len(sections)
        if s_len > len(self.actions):
            return

        if 'fold' == self.actions[-1].action:
            return

        for i in range(1, s_len):
            is_pool_raised = sections[i - 1].pool < sections[i].pool
            pre_action = self.actions[i - 1].action

            if 'pending' in pre_action:
                if is_pool_raised:
                    if self.actions[i - 1].amount <= self.actions[i].amount:
                        self.actions[i - 1].action = 'fold'
                else:
                    self.actions[i - 1].action = 'check'
            else:
                self.actions[i].action = 'check'

    @staticmethod
    def eval_action(pre_amount, cur_amount, pre_pool, cur_pool, is_other_bet_behind):
        is_pool_raised = cur_pool > pre_pool
        if not is_other_bet_behind:
            if is_pool_raised:
                if cur_amount >= pre_amount:
                    # 底池增加，玩家的金额未减少，表示: fold
                    return 'fold'
                else:
                    # 底池增加，玩家的金额未减少，表示: fold
                    return 'bet:{}'.format(pre_amount - cur_amount)




class PlayerAction:
    player_id = IntegerField()
    stage = CharField()
    round = IntegerField()
    action = CharField()
    amount = DecimalField()


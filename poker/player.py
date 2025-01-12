from models.base import BaseModel, db
from flask_peewee.db import CharField, IntegerField, DateTimeField, AutoField, DecimalField


class Player(BaseModel):
    id = AutoField()
    game_code = CharField()
    name = CharField()
    seat = CharField()
    balance = DecimalField()  # 余额
    actions = []


class PlayerAction:
    player_id = IntegerField()
    stage = CharField()
    round = IntegerField()
    action = CharField()
    amount = DecimalField()


def eval_player_actions(sections, idx):
    actions = []
    for i in range(len(sections)):
        pa = PlayerAction()
        sec = sections[i]
        pool = sec.pool
    return actions

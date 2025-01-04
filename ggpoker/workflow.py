import time

from entities import Game, Section, Action
from strategy import do_action
from utils import *


class WorkFlow:

    def __init__(self):
        self.ocr = ddddocr.DdddOcr()

        # 过牌位置
        # self.action_check_position = (1052, 852)
        # self.action_check_bgr = (159, 55, 52)
        self.game = None
        self.action = Action()

    def read_new_section(self):
        if not location_by_color('table'):
            # 没有牌桌
            return
        pool = read_pool(self.ocr)
        if not pool:
            # 没有底池
            return
        card1 = read_card(self.ocr, 1)
        if not card1:
            # 没有手牌
            return
        card2 = read_card(self.ocr, 2)
        if self.game is None:
            self.game = Game.new(card1, card2, 0)
        sec = Section()
        sec.pool = pool
        sec.card3 = read_card(self.ocr, 3)
        if sec.card3:
            sec.card4 = read_card(self.ocr, 4)
            sec.card5 = read_card(self.ocr, 5)
            sec.card6 = read_card(self.ocr, 6)
            if sec.card6:
                sec.card7 = read_card(self.ocr, 7)
        if self.game.sections:
            last_section = self.game.sections[-1]
            if not last_section.equals(sec):
                self.game.add_section(sec)
                return sec
        else:
            self.game.add_section(sec)
            return sec

    def read_players(self):
        if self.game.sections:
            section = self.game.sections[-1]
            if len(self.game.sections) > 1 and self.game.sections[-2].pool == section.pool:
                # 底池没变化，不再次读取玩家信息
                return
            else:
                section.player1 = read_player(self.ocr, 1)
                section.player2 = read_player(self.ocr, 2)
                section.player3 = read_player(self.ocr, 3)
                section.player4 = read_player(self.ocr, 4)
                section.player5 = read_player(self.ocr, 5)


    def is_action(self):
        # image = Image.open(DESKTOP_IMAGE)
        # color = image.getpixel(FOLD_BUTTON_POSITION)
        color = pyautogui.pixel(FOLD_BUTTON_POSITION[0], FOLD_BUTTON_POSITION[1])
        return not is_match_color(BACKGROUND_COLOR, color, 50)

    def start(self):
        while True:
            if shot_table_image():
                new_section = self.read_new_section()
                if new_section:
                    self.read_players()
                do_action(self.game)
            time.sleep(3)


wf = WorkFlow()
# ocr_desktop.read_card(1)
# ocr_desktop.read_card(2)
wf.start()

# rec_color(830, 860)

# color = pyautogui.pixel(READ_FLAG_POSITION[0], READ_FLAG_POSITION[1])
# print(color)

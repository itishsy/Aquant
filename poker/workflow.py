import time
import io

from poker.game import Game, Section, Action
from poker.player import PlayerAction
from poker.utils import *
from poker.strategy import Strategy


class TableImage:

    def __init__(self, image, ocr):
        self.image = image
        self.ocr = ocr
        self.section = None

    def is_open(self):
        color = self.image.getpixel(POSITION_READY)
        return is_match_color(color, COLOR_READY, 50)

    def ocr_txt(self, region):
        x1 = WIN_OFFSET[0] + region[0]
        y1 = WIN_OFFSET[1] + region[1]
        x2 = WIN_OFFSET[0] + region[0] + region[2]
        y2 = WIN_OFFSET[1] + region[1] + region[3]
        # self.image.save("aaa.jpg")
        region_image = self.image.crop((x1, y1, x2, y2))
        # region_image.save(cropped_image)
        image_bytes = io.BytesIO()
        region_image.save(image_bytes, format='PNG')
        image_bytes = image_bytes.getvalue()
        result = self.ocr.classification(image_bytes)
        return result

    def fetch_card(self, idx):
        region = get_region('CARD', idx)
        ocr_txt = self.ocr_txt(region)
        card_text = fetch_card(ocr_txt, idx)
        if card_text is not None:
            if idx > 3:
                suit_position = (POSITION_SUIT_3[0] + PUB_CARD_SPACE_X*(idx-3), POSITION_SUIT_3[1])
            else:
                suit_position = eval('POSITION_SUIT_' + str(idx))
            color = self.image.getpixel(suit_position)
            if is_match_color(SUIT_COLOR[0], color, 20):
                return card_text + 's'
            if is_match_color(SUIT_COLOR[1], color, 20):
                return card_text + 'h'
            if is_match_color(SUIT_COLOR[2], color, 20):
                return card_text + 'c'
            if is_match_color(SUIT_COLOR[3], color, 20):
                return card_text + 'd'

    def fetch_player(self, idx):
        (region_name, region_amount) = get_region('PLAYER', idx)
        name = self.ocr_txt(region_name)
        amount_txt = self.ocr_txt(region_amount)
        amount = fetch_amount(amount_txt)
        return name, amount

    def fetch_pool(self):
        region = get_region('POOL')
        ocr_txt = self.ocr_txt(region)
        return fetch_amount(ocr_txt)

    def fetch_seat(self):
        for i in range(6):
            position = eval('POSITION_BOTTOM_' + str(i))
            color = self.image.getpixel(position)
            if is_match_color(COLOR_BOTTOM, color, 50):
                return 6 - i
        return -1

    def create_section(self):
        pool = self.fetch_pool()
        card1 = self.fetch_card(1)
        seat = self.fetch_seat()
        if not pool or not card1 or not seat:
            return

        sec = Section()
        sec.pool = pool
        sec.seat = seat
        sec.card1 = card1
        sec.card2 = self.fetch_card(2)
        sec.card3 = self.fetch_card(3)
        if sec.card3:
            sec.card4 = self.fetch_card(4)
            sec.card5 = self.fetch_card(5)
            sec.card6 = self.fetch_card(6)
            if sec.card6:
                sec.card7 = self.fetch_card(7)

        sec.player1, sec.player1_amount = self.fetch_player(1)
        sec.player2, sec.player2_amount = self.fetch_player(2)
        sec.player3, sec.player3_amount = self.fetch_player(3)
        sec.player4, sec.player4_amount = self.fetch_player(4)
        sec.player5, sec.player5_amount = self.fetch_player(5)

        if not self.section.equals(sec):
            self.section = sec
            return sec


class WorkFlow:

    def __init__(self):
        self.ocr = ddddocr.DdddOcr()
        self.game = Game()
        self.win = None
        self.is_start = False
        self.image = None
        self.game_sections_size = 0
        self.game_info = ''

    def active(self):
        if not self.is_start:
            win = get_win()
            if win:
                self.win = win
                img = pyautogui.screenshot(region=(win.left, win.top, win.width, win.height))
                self.is_start = is_match_color(img.getpixel(POSITION_READY), COLOR_READY)
        if self.is_start:
            image = pyautogui.screenshot(region=(self.win.left, self.win.top, self.win.width, self.win.height))
            if is_match_color(image.getpixel(POSITION_FOLD_BUTTON), COLOR_BUTTON):
                self.image = image
                return True
        return False

    def load(self, sec):
        """
        检查一个新的section是否合格，避免重复添加到game中
        :param sec:
        :return:
        """
        flag = False
        if sec and sec.card1 and sec.card2 and sec.seat:
            if self.game.card1 != sec.card1 or self.game.card2 != sec.card2 or self.game.seat != sec.seat:
                self.game = Game.create_by_section(sec)
                flag = True
            elif not sec.equals(self.game.sections[-1]):
                self.game.append_section(sec)
                flag = True
            # if flag:
            #     for i in range(5):
            #         player = self.game.players[i]
            #         if player.status == 'playing' and player.actions[-1].action != 'fold':
            #             act = PlayerAction()
            #             act.stage = sec.get_stage()
            #             act.round = 1 if player.actions[-1].stage != act.stage else player.actions[-1].round + 1
            #             act.amount = eval('sec.player{}_amount'.format(i-1))
            #             act.action = 'pending'
            #             player.actions.append(act)
            #             player.eval_player_actions(self.game.sections, i)
        return flag

    def do_action(self):
        self.print()
        act = self.game.get_action()
        if act:
            print("\t操作：{}".format(act))

    def print(self):
        size = len(self.game.sections)
        if size == 1:
            if self.game_info != self.game.get_info():
                print('\n------------', self.game.get_info(), '------------')
                self.game_info = self.game.get_info()
            self.game_sections_size = 1
        else:
            for i in range(self.game_sections_size, size):
                sec = self.game.sections[i]
                if sec.card3:
                    print("{}: {}|{}|{}|{}|{} pool: {}".format(sec.get_stage(), sec.card3, sec.card4, sec.card5,
                                                               sec.card6, sec.card7, sec.pool))
                if sec.player1 and sec.player1_action and 'bet' in sec.player1_action:
                    print("\tplayer1:\t{}({}),{}".format(
                        sec.player1, sec.player1_amount, sec.player1_action))
                if sec.player2 and sec.player2_action and 'bet' in sec.player2_action:
                    print("\tplayer2:\t{}({}),{}".format(
                        sec.player2, sec.player2_amount, sec.player2_action))
                if sec.player3 and sec.player3_action and 'bet' in sec.player3_action:
                    print("\tplayer3:\t{}({}),{}".format(
                        sec.player3, sec.player3_amount, sec.player3_action))
                if sec.player4 and sec.player4_action and 'bet' in sec.player4_action:
                    print("\tplayer4:\t{}({}),{}".format(
                        sec.player4, sec.player4_amount, sec.player4_action))
                if sec.player5 and sec.player5_action and 'bet' in sec.player5_action:
                    print("\tplayer5:\t{}({}),{}".format(
                        sec.player5, sec.player5_amount, sec.player5_action))
            self.game_sections_size = size

    def start(self):
        while True:
            if self.active():
                table = TableImage(self.image, self.ocr)
                section = table.create_section()
                if section and self.load(section):
                    strategy = Strategy(self.game)
                    strategy.predict()
                    self.do_action()
                else:
                    print('error section:' + section.to_string())
            else:
                print('未开始游戏')
            time.sleep(3)


def test_workflow(file_name='table_image.jpg'):
    wf1 = WorkFlow()
    tab1 = TableImage(Image.open(file_name), wf1.ocr)
    sec1 = tab1.create_section()
    if wf1.load(sec1):
        wf1.print()


if __name__ == '__main__':
    wf = WorkFlow()
    wf.start()
    # test_workflow()


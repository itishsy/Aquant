import time
import io
from datetime import datetime
from entities import Game, Section, Action
from utils import *
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
        region_image.save(cropped_image)
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
                suit_position = (POSITION_SUIT_3[0] + PUB_CARD_SPACE_X, POSITION_SUIT_3[1])
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
        if not pool:
            print('无法读取底池')
            return
        card1 = self.fetch_card(1)
        if not card1:
            print('无法读取手牌')
            return
        card2 = self.fetch_card(2)
        sec = Section()
        sec.pool = pool
        sec.seat = self.fetch_seat()
        sec.card1 = card1
        sec.card2 = card2
        sec.card3 = self.fetch_card(3)
        if sec.card3:
            sec.card4 = self.fetch_card(4)
            sec.card5 = self.fetch_card(5)
            sec.card6 = self.fetch_card(6)
            if sec.card6:
                sec.card7 = self.fetch_card(7)
        self.section = sec
        return sec

    def fetch_players(self):
        if self.section:
            self.section.player1, self.section.player1_amount = self.fetch_player(1)
            self.section.player2, self.section.player2_amount = self.fetch_player(2)
            self.section.player3, self.section.player3_amount = self.fetch_player(3)
            self.section.player4, self.section.player4_amount = self.fetch_player(4)
            self.section.player5, self.section.player5_amount = self.fetch_player(5)


class WorkFlow:

    def __init__(self):
        self.ocr = ddddocr.DdddOcr()
        self.game = Game()
        self.is_active = False
        self.win = None
        self.game_info = None

    def active(self):
        if not self.is_active:
            win = get_win()
            if win:
                self.win = win
                img = pyautogui.screenshot(region=(win.left, win.top, win.width, win.height))
                color = img.getpixel(POSITION_READY)
                self.is_active = is_match_color(color, COLOR_READY, 50)
        return self.is_active

    def load(self, sec):
        """
        检查一个新的section是否合格，避免重复添加到game中
        :param sec:
        :return:
        """
        if sec is None:
            return False

        if not sec.card1 or not sec.card2 or not sec.seat:
            return False

        # print(sec.to_string())
        if self.game:
            if self.game.card1 != sec.card1 or self.game.card2 != sec.card2 or self.game.seat != sec.seat:
                game = Game()
                game.code = datetime.now().strftime('%Y%m%d%H%M%S')
                game.card1 = sec.card1
                game.card2 = sec.card2
                game.seat = sec.seat
                game.stage = sec.get_stage()
                game.created = datetime.now()
                self.game = game
                self.game.sections.append(sec)
                return True
            if self.game.sections:
                last_sec = self.game.sections[-1]
                if last_sec.equals(sec):
                    return False
                else:
                    self.game.sections.append(sec)
        return True

    def reload(self, sec):
        if self.game and self.game.sections:
            last_sec = self.game.sections[-1]
            if last_sec.equals(sec):
                self.game.sections[-1] = sec
            else:
                self.game.sections.append(sec)

    def action(self):
        act = Action.Null
        if self.game.sections:
            if not self.game.sections[-1].action:
                strategy = Strategy(self.game)
                strategy.analyze()
                act = strategy.cal()
                self.game.sections[-1].action = act
            else:
                act = self.game.sections[-1].action
        return act

    def print(self):
        game_info = self.game.to_strings()
        if self.game_info != game_info:
            self.game_info = game_info
            for msg in game_info:
                print(msg)

    def start(self):
        while True:
            if self.active():
                image = pyautogui.screenshot(region=(self.win.left, self.win.top, self.win.width, self.win.height))
                table = TableImage(image, self.ocr)
                section = table.create_section()
                if self.load(section):
                    table.fetch_players()
                    self.reload(section)
                    self.action()
                self.print()
            else:
                print('未进入游戏桌面')
            time.sleep(3)


def test_workflow(file_name='table_image.jpg'):
    wf1 = WorkFlow()
    tab1 = TableImage(Image.open(file_name), wf1.ocr)
    sec1 = tab1.create_section()
    if wf1.load(sec1):
        tab1.fetch_players()
        wf1.reload(sec1)
        wf1.action()
    wf1.print()


if __name__ == '__main__':
    wf = WorkFlow()
    wf.start()
    # test_workflow()


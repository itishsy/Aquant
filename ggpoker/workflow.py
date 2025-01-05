import time
import io

from entities import Game, Section
from strategy import do_action
from utils import *


class TableImage:

    def __init__(self, w, ocr):
        self.image = Image.open(w) if isinstance(w, str) else (
            pyautogui.screenshot(region=(w.left, w.top, w.width, w.height)))
        self.ocr = ocr

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

    def section(self):
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
        return sec

    def set_players(self, section):
        if section:
            name1, amount1 = self.fetch_player(1)
            section.player1 = 'name:{},amount:{}'.format(name1, amount1)
            name2, amount2 = self.fetch_player(2)
            section.player2 = 'name:{},amount:{}'.format(name2, amount2)
            name3, amount3 = self.fetch_player(3)
            section.player3 = 'name:{},amount:{}'.format(name3, amount3)
            name4, amount4 = self.fetch_player(4)
            section.player4 = 'name:{},amount:{}'.format(name4, amount4)
            name5, amount5 = self.fetch_player(5)
            section.player5 = 'name:{},amount:{}'.format(name5, amount5)


class WorkFlow:

    def __init__(self):
        self.ocr = ddddocr.DdddOcr()
        self.active = False
        self.win = None
        self.game = None

    def check(self, section):
        if section is None:
            return False

        print(section.to_string())
        if self.game:
            if self.game.card1 != section.card1 or self.game.card2 != section.card2 or self.game.seat != section.seat:
                self.game = Game.new(section.card1, section.card2, section.seat)
                return True
            if self.game.sections:
                last_section = self.game.sections[-1]
                return not last_section.equals(section)
        else:
            self.game = Game.new(section.card1, section.card2, section.seat)
            return True

    def is_active(self):
        if not self.active:
            win = get_win()
            if win:
                self.win = win
                self.active = True  # match_position('TABLE', is_desktop=True)
        return self.active

    def start(self):
        while True:
            if self.is_active():
                table = TableImage(self.win, self.ocr)
                if table.is_open():
                    section = table.section()
                    if self.check(section):
                        table.set_players(section)
                        self.game.load(section)
                        self.game.print()
                    act = do_action(self.game)
                    print('action:', act)
            else:
                print('未进入游戏桌面')
            time.sleep(3)


def test_ocr_table_image(img='table_image.jpg'):
    tab1 = TableImage(img, ddddocr.DdddOcr())
    sec1 = tab1.section()
    tab1.set_players(sec1)
    print(sec1.to_string())


wf = WorkFlow()
wf.start()


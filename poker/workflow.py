import time
import io
import random

from poker.game import Game, Section, Action
from poker.player import PlayerAction
from poker.utils import *
from poker.strategy import Strategy003


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

        return sec


class WorkFlow:

    def __init__(self):
        self.ocr = ddddocr.DdddOcr()
        self.game = Game()
        self.win = None
        self.is_start = False
        self.section = None
        self.game_sections_size = 0
        self.game_info = ''

    def active(self):
        if self.is_start:
            image = pyautogui.screenshot(region=(self.win.left, self.win.top, self.win.width, self.win.height))
            # image.save(table_image)
            if is_match_color(image.getpixel(POSITION_BUTTON_FOLD), COLOR_BUTTON):
                table = TableImage(image, self.ocr)
                sec = table.create_section()
                if sec and not self.section or not sec.equals(self.game.sections[-1]):
                    self.section = sec
                    return True
        else:
            win = get_win()
            if win and (win.left > 0 or win.top > 0):
                self.win = win
                img = pyautogui.screenshot(region=(win.left, win.top, win.width, win.height))
                self.is_start = is_match_color(img.getpixel(POSITION_READY), COLOR_READY)
                if self.is_start:
                    print("start")
                    return self.active()
                else:
                    print("ready")
            else:
                print("no window")
        return False

    def load(self):
        """
        检查一个新的section是否合格，避免重复添加到game中
        :return:
        """
        if self.section and self.section.card1 and self.section.card2 and self.section.seat:
            if self.game.card1 != self.section.card1 or self.game.card2 != self.section.card2 or self.game.seat != self.section.seat:
                self.game = Game.create_by_section(self.section)
                return True
            elif not self.section.equals(self.game.sections[-1]):
                self.game.append_section(self.section)
                return True
        return False

    def do_action(self):
        strategy = Strategy003(self.game)
        strategy.predict()
        self.print()
        if self.game.action:
            print(self.game.action)
            # 移动鼠标到指定位置
            if self.game.action == 'Fold':
                pyautogui.moveTo(POSITION_BUTTON_FOLD[0]+random.randint(1, 10), POSITION_BUTTON_FOLD[1] + random.randint(1, 5), duration=0.5)  # duration 参数表示鼠标移动的时间，这里设置为 1 秒
            elif self.game.action == 'Call':
                pyautogui.moveTo(POSITION_BUTTON_CALL[0]+random.randint(1, 10), POSITION_BUTTON_CALL[1] + random.randint(1, 5), duration=0.5)  # duration 参数表示鼠标移动的时间，这里设置为 1 秒
            elif self.game.action == 'Raise':
                pyautogui.moveTo(POSITION_BUTTON_RAISE[0]+random.randint(1, 10), POSITION_BUTTON_RAISE[1] + random.randint(1, 5), duration=0.5)  # duration 参数表示鼠标移动的时间，这里设置为 1 秒
            self.game.action = None
            pyautogui.click()
            pyautogui.moveTo(POSITION_BUTTON_FOLD[0]+random.randint(1, 10), POSITION_BUTTON_FOLD[1] + random.randint(100, 150)-300,
                             duration=0.5)  # duration 参数表示鼠标移动的时间，这里设置为 1 秒

    def print(self):
        if not self.game_info or self.game_info != self.game.get_info():
            self.game_info = self.game.get_info()
            print('-----', self.game_info, '-----')

        sec = self.game.sections[-1]
        if sec.card3:
            print("pool: {}, 公共牌: {}-{}-{}-{}-{}".format(
                sec.pool, self.game.card3, self.game.card4, self.game.card5,
                self.game.card6, self.game.card7))
        else:
            print("pool: {}".format(sec.pool))

        if len(self.game.sections) > 1:
            for player in self.game.players:
                if player.actions and player.actions[-1].action != 'fold':
                    print("{}: {}, {}".format(player.name, player.seat, player.actions[-1].action))

    def start(self):
        while True:
            if self.active():
                if self.load():
                    self.do_action()
            time.sleep(3)


def test_workflow(file_name='table_image.jpg'):
    wf1 = WorkFlow()
    tab1 = TableImage(Image.open(file_name), wf1.ocr)
    wf1.section = tab1.create_section()
    if wf1.load():
        wf1.print()


if __name__ == '__main__':
    wf = WorkFlow()
    wf.start()
    # test_workflow()


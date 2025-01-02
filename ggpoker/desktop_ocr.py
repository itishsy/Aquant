import pyautogui
import ddddocr
from PIL import Image
import time
from desktop_info import DesktopInfo
from decimal import Decimal
from actions import Action
from config import *


# 需要远程到游戏桌面, 远程桌面分辩设置为：1440*900
# 游戏窗口最大化，牌需要设置为4色


def is_match_color(color1, color2, diff):
    return (abs(color1[0] - color2[0]) < diff and
            abs(color1[1] - color2[1]) < diff and
            abs(color1[1] - color2[1]) < diff)


def rec_color(x, y):
    image = Image.open("desktop_image.jpg")
    color = image.getpixel((x, y))
    print(color)


class OcrDesktop:

    def __init__(self):
        self.ocr = ddddocr.DdddOcr()
        
        # 手牌区域
        self.card1_region = (CARD_ONE_POSITION[0], CARD_ONE_POSITION[1], CARD_WIDTH, CARD_HEIGHT)
        self.card2_region = (CARD_TWO_POSITION[0], CARD_TWO_POSITION[1], CARD_WIDTH, CARD_HEIGHT)

        # 公共牌区域
        self.card3_region = (PUB_CARD_POSITION[0], PUB_CARD_POSITION[1], CARD_WIDTH, CARD_HEIGHT)
        self.card4_region = (PUB_CARD_POSITION[0] + PUB_CARD_SPACE_X, PUB_CARD_POSITION[1], CARD_WIDTH, CARD_HEIGHT)
        self.card5_region = (PUB_CARD_POSITION[0] + PUB_CARD_SPACE_X*2, PUB_CARD_POSITION[1], CARD_WIDTH, CARD_HEIGHT)
        self.card6_region = (PUB_CARD_POSITION[0] + PUB_CARD_SPACE_X*3, PUB_CARD_POSITION[1], CARD_WIDTH, CARD_HEIGHT)
        self.card7_region = (PUB_CARD_POSITION[0] + PUB_CARD_SPACE_X*4, PUB_CARD_POSITION[1], CARD_WIDTH, CARD_HEIGHT)
        self.suit3_position = (PUB_SUIT_OFFSET[0], PUB_SUIT_OFFSET[1])
        self.suit4_position = (PUB_SUIT_OFFSET[0]+PUB_CARD_SPACE_X, PUB_SUIT_OFFSET[1])
        self.suit5_position = (PUB_SUIT_OFFSET[0]+PUB_CARD_SPACE_X*2, PUB_SUIT_OFFSET[1])
        self.suit6_position = (PUB_SUIT_OFFSET[0]+PUB_CARD_SPACE_X*3, PUB_SUIT_OFFSET[1])
        self.suit7_position = (PUB_SUIT_OFFSET[0]+PUB_CARD_SPACE_X*4, PUB_SUIT_OFFSET[1])

        # 过牌位置
        self.action_check_position = (1052, 852)
        self.action_check_bgr = (159, 55, 52)

        self.desktop = DesktopInfo()
        self.action = Action()

    def shot(self):
        wins = pyautogui.getWindowsWithTitle(WIN_TITLE)
        if wins:
            win = wins[0]
            # if not win.isActive:
            #     win.activate()
            screenshot = pyautogui.screenshot(region=(win.left, win.top, win.width, win.height))
            screenshot.save(DESKTOP_IMAGE)

    def crop(self, left, top, width, height):
        image = Image.open(DESKTOP_IMAGE)
        x_min = OFFSET_X + left
        y_min = OFFSET_Y + top
        x_max = OFFSET_X + left + width
        y_max = OFFSET_Y + top + height
        cropped_image = image.crop((x_min, y_min, x_max, y_max))
        # 保存截取后的图片
        cropped_image.save(CROPPED_IMAGE)

    def rec_text(self):
        image = open(CROPPED_IMAGE, "rb").read()
        result = self.ocr.classification(image)
        return result

    def rec_suit(self, x, y):
        # 黑桃（Spade）红桃（Heart）梅花（Club）方块（Diamond）
        image = Image.open(DESKTOP_IMAGE)
        color = image.getpixel((x, y))
        # print(f"位置({x}, {y})，RGB值为：{b, g, r}")
        if is_match_color(SPADE_COLOR, color, 20):
            return 's'
        if is_match_color(HEART_COLOR, color, 20):
            return 'h'
        if is_match_color(CLUB_COLOR, color, 20):
            return 'c'
        if is_match_color(DIAMOND_COLOR, color, 20):
            return 'd'
        return '?'

    def fetch_card_number(self, txt):
        for c in OCR_CARDS:
            if c in txt:
                if c == '10' or c == '1O' or c == '1o':
                    return 'T'
                if c == 'j':
                    return 'J'
                if c == 'k':
                    return 'K'
                else:
                    return c

    def read_card(self, idx):
        region = eval('self.card' + str(idx) + '_region')
        self.crop(region[0], region[1], region[2], region[3])
        txt = self.rec_text()
        card = self.fetch_card_number(txt)
        if card:
            if idx == 1:
                suit_position = SUIT_ONE_POSITION
            elif idx == 2:
                suit_position = SUIT_TWO_POSITION
            else:
                suit_position = eval('self.suit' + str(idx) + '_position')
            suit = self.rec_suit(suit_position[0], suit_position[1])
            return card + suit

    def read_pool(self):
        self.crop(POOL_REGION[0], POOL_REGION[1], POOL_REGION[2], POOL_REGION[3])
        txt = self.rec_text()
        if txt:
            txt = txt.replace("o", "0")
            txt = txt.replace("O", "0")
            length = len(txt)
            part1 = txt[1: length - 2]
            part2 = txt[length - 2: length]
            val = '{}.{}'.format(part1, part2)
            print('pool:', txt)
            return Decimal(val)
        return 0.00

    def get_stage(self):
        if not self.desktop.card3:
            return STAGE.PreFlop
        elif not self.desktop.card6:
            return STAGE.Flop
        elif not self.desktop.card7:
            return STAGE.Turn
        return STAGE.River

    def do_action(self):
        stage = self.get_stage()
        act = None
        if stage == STAGE.PreFlop:
            act = self.action.pre_flop()
        elif stage == STAGE.Flop:
            act = self.action.flop()
        elif stage == STAGE.River:
            act = self.action.river()
        elif stage == STAGE.Turn:
            act = self.action.turn()

        print(act)
        if act == ACT.Fold:
            pyautogui.click(FOLD_BUTTON_POSITION[0], FOLD_BUTTON_POSITION[1])
            pyautogui.moveRel(100, 100)

    def is_read(self):
        color = pyautogui.pixel(READ_FLAG_POSITION[0], READ_FLAG_POSITION[1])
        if is_match_color(READ_FLAG_COLOR, color, 10):
            self.shot()
            return True
        return False

    def is_action(self):
        # image = Image.open(DESKTOP_IMAGE)
        # color = image.getpixel(FOLD_BUTTON_POSITION)
        color = pyautogui.pixel(FOLD_BUTTON_POSITION[0], FOLD_BUTTON_POSITION[1])
        return not is_match_color(BACKGROUND_COLOR, color, 50)

    def read(self):
        new_desktop = None
        if self.is_read():
            new_desktop = DesktopInfo()
            new_desktop.card1 = self.read_card(1)
            if new_desktop.card1:
                new_desktop.card2 = self.read_card(2)
                new_desktop.card3 = self.read_card(3)
            if new_desktop.card3:
                new_desktop.card4 = self.read_card(4)
                new_desktop.card5 = self.read_card(5)
                new_desktop.card6 = self.read_card(6)
            if new_desktop.card6:
                new_desktop.card7 = self.read_card(7)
            new_desktop.pool = self.read_pool()
            if self.desktop is None:
                self.desktop = new_desktop
        if new_desktop and not self.desktop.equals(desktop_info=new_desktop):
            self.action.add(new_desktop)
            self.desktop = new_desktop
            print(new_desktop.to_string(), 'action:', self.is_action())
        if self.is_action():
            self.do_action()


ocr_desktop = OcrDesktop()
# ocr_desktop.read_card(1)
# ocr_desktop.read_card(2)
while True:
    ocr_desktop.read()
    time.sleep(3)

# rec_color(830, 860)

# color = pyautogui.pixel(READ_FLAG_POSITION[0], READ_FLAG_POSITION[1])
# print(color)

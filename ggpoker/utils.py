import pyautogui
import ddddocr
from PIL import Image
from config import *
from decimal import Decimal


table_image = "table_image.jpg"
cropped_image = 'table_cropped_image.jpg'
ocr_cards = ['A', 'K', 'k', 'Q', 'J', 'j', '10', '1o', '1O', '9', '8', '7', '6', '5', '4', '3', '2']


def shot_table_image():
    wins = pyautogui.getWindowsWithTitle(WIN_TITLE)
    if wins:
        win = wins[0]
        # if not win.isActive:
        #     win.activate()
        screenshot = pyautogui.screenshot(region=(win.left, win.top, win.width, win.height))
        screenshot.save(table_image)
        return True
    return False


def crop_table_image(left, top, width, height):
    image = Image.open(table_image)
    x_min = OFFSET_X + left
    y_min = OFFSET_Y + top
    x_max = OFFSET_X + left + width
    y_max = OFFSET_Y + top + height
    image.crop((x_min, y_min, x_max, y_max)).save(cropped_image)


def is_match_color(color1, color2, diff):
    return (abs(color1[0] - color2[0]) < diff and
            abs(color1[1] - color2[1]) < diff and
            abs(color1[1] - color2[1]) < diff)


def fetch_color(x, y, is_win_desktop=False):
    if is_win_desktop:
        return pyautogui.pixel(x, x)
    image = Image.open(table_image)
    color = image.getpixel((x, y))
    return color


def location_by_color(name, color_diff=30):
    position = eval(name.upper()+'_POSITION')
    color = eval(name.upper()+'_COLOR')
    return is_match_color(fetch_color(position[0], position[1]), color, color_diff)


def ocr_text(ocr, region):
    crop_table_image(region[0], region[1], region[2], region[3])
    image = open(cropped_image, "rb").read()
    txt = ocr.classification(image)
    return txt


def read_card(ocr, idx):
    idx_str = str(idx)
    if idx > 3:
        idx_str = '3'
    location = eval('CARD_' + idx_str + '_LOCATION')
    card_region = location[0]
    if idx > 3:
        card_region = (card_region[0] + (idx-3)*PUB_CARD_SPACE_X, card_region[1], card_region[2], card_region[3])
    ocr_txt = ocr_text(ocr, card_region)
    card_txt = None
    for c in ocr_cards:
        if c in ocr_txt:
            if c == '10' or c == '1O' or c == '1o':
                card_txt = 'T'
            elif c == 'j':
                card_txt = 'J'
            elif c == 'k':
                card_txt = 'K'
            else:
                card_txt = c
            break
    if card_txt is not None:
        suit_position = location[1]
        color = fetch_color(suit_position[0], suit_position[1])
        if is_match_color(SUIT_COLOR[0], color, 20):
            return card_txt + 's'
        if is_match_color(SUIT_COLOR[1], color, 20):
            return card_txt + 'h'
        if is_match_color(SUIT_COLOR[2], color, 20):
            return card_txt + 'c'
        if is_match_color(SUIT_COLOR[3], color, 20):
            return card_txt + 'd'


def read_pool(ocr):
    ocr_txt = ocr_text(ocr, POOL_REGION)
    if ocr_txt:
        ocr_txt = ocr_txt.replace("o", "0")
        ocr_txt = ocr_txt.replace("O", "0")
        length = len(ocr_txt)
        part1 = ocr_txt[1: length - 2]
        part2 = ocr_txt[length - 2: length]
        val = '{}.{}'.format(part1, part2)
        # print('pool:', txt)
        return Decimal(val)
    return 0.00


def read_player(ocr, idx):
    return None


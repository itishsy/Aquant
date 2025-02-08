import pyautogui
from PIL import Image
from config import *
from decimal import Decimal

table_image = "table_image.jpg"
cropped_image = 'table_cropped_image.jpg'
ocr_cards = ['A', 'K', 'k', 'Q', 'J', 'j', '10', '1o', '1O', '9', '8', '7', '6', '5', '4', '3', '2']


def get_win():
    wins = pyautogui.getWindowsWithTitle(WIN_TITLE)
    if wins:
        return wins[0]


def shot_table_image(is_save=False):
    win = get_win()
    if win:
        # if not win.isActive:
        #     win.activate()
        screenshot = pyautogui.screenshot(region=(win.left, win.top, win.width, win.height))
        if is_save:
            screenshot.save(table_image)
        return table_image


def crop_table_image(left, top, width, height):
    image = Image.open(table_image)
    x_min = WIN_OFFSET[0] + left
    y_min = WIN_OFFSET[1] + top
    x_max = WIN_OFFSET[0] + left + width
    y_max = WIN_OFFSET[1] + top + height
    region_image = image.crop((x_min, y_min, x_max, y_max))
    region_image.save(cropped_image)


def is_match_color(color1, color2, diff=100):
    return (abs(color1[0] - color2[0]) < diff and
            abs(color1[1] - color2[1]) < diff and
            abs(color1[2] - color2[2]) < diff)


def fetch_color(x, y, is_desktop=False):
    if is_desktop:
        return pyautogui.pixel(x, x)
    image = Image.open(table_image)
    color = image.getpixel((x, y))
    return color


def match_position(name, color_diff=50, is_desktop=False):
    position = eval('POSITION_' + name.upper())
    color = eval('COLOR_' + name.upper())
    position_color = fetch_color(position[0], position[1], is_desktop=is_desktop)
    return is_match_color(position_color, color, color_diff)


def ocr_text(ocr, region):
    crop_table_image(region[0], region[1], region[2], region[3])
    image = open(cropped_image, "rb").read()
    txt = ocr.classification(image)
    return txt


def fetch_card(ocr_txt, idx):
    card_txt = None
    # print(ocr_txt)
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
    return card_txt


def fetch_amount(ocr_txt):
    if ocr_txt and '全押' not in ocr_txt:
        ocr_txt = ocr_txt.replace("o", "0")
        ocr_txt = ocr_txt.replace("O", "0")
        length = len(ocr_txt)
        if length == 2:
            part1 = ocr_txt[1:]
            val = '{}.00'.format(part1)
        else:
            part1 = ocr_txt[1: length - 2]
            part2 = ocr_txt[length - 2: length]
            val = '{}.{}'.format(part1, part2)
        # print('amount:', ocr_txt)
        try:
            return float(val)
        except:
            return 0.0
    return 0.0


def get_region(name, idx=None):
    if name == 'CARD' or name == 'SUIT':
        idx_str = '3' if idx > 3 else str(idx)
        region = eval('REGION_' + name + '_' + idx_str)
        if idx > 3:
            region = (region[0] + (idx - 3) * PUB_CARD_SPACE_X, region[1], region[2], region[3])
        return region
    elif name == 'PLAYER':
        name_region = eval('REGION_PLAYER_' + str(idx))
        amount_region = (name_region[0], name_region[1] + PLAYER_HEIGHT - 5, name_region[2], name_region[3])
        return name_region, amount_region
    elif idx:
        return eval('REGION_' + name + '_' + str(idx))
    else:
        return eval('REGION_' + name)

# shot_table_image(True)

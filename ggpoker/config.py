class STAGE:
    PreFlop = 0
    Flop = 1
    Turn = 2
    River = 3


class ACT:
    Fold = -1
    Check = 0
    Call = 1
    Raise = 2
    AllIn = 100


OCR_CARDS = ['A', 'K', 'Q', 'J', '10', '9', '8', '7', '6', '5', '4', '3', '2']
RAISE_CARDS = ['AA', 'KK']
CALL_CARDS = ['AK', 'AQ', 'AJ', 'AT', 'KQ',
              'QQ', 'JJ', 'TT', '99', '88', '77', '66', '55', '44', '33', '22']
CALL_CARD_SUITS = ['A9', 'A8', 'A7', 'A6', 'A5', 'A4', 'A3', 'A2',
                   'KJ', 'KT', 'QJ', 'QT', 'Q9', 'JT', 'J9', 'T9']

WIN_TITLE = "192.168.0.113 - 远程桌面连接"
DESKTOP_IMAGE = "desktop_image.jpg"
CROPPED_IMAGE = 'cropped_image.jpg'

# 截图偏移
OFFSET_X, OFFSET_Y = 0, 0
# 单个牌要截取的宽度和高度
CARD_WIDTH, CARD_HEIGHT = 35, 40

# 第1张手牌起始位置
CARD_ONE_POSITION = (655, 696)
# 第1张手牌花色位置
SUIT_ONE_POSITION = (676, 751)

# 第2张手牌起始位置
CARD_TWO_POSITION = (721, 692)
# 第2张手牌花色位置
SUIT_TWO_POSITION = (737, 746)

# 第1张公共牌起始位置
PUB_CARD_POSITION = (488, 410)
# 第1张公共牌花色位置
PUB_SUIT_OFFSET = (546, 486)
# 公共牌之间的间隔
PUB_CARD_SPACE_X = 100

# 底池区域
POOL_REGION = (729, 368, 88, 30)

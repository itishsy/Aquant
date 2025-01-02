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


OCR_CARDS = ['A', 'K', 'k', 'Q', 'J', 'j', '10', '1o', '1O', '9', '8', '7', '6', '5', '4', '3', '2']
RAISE_CARDS = ['AA', 'KK']
CALL_CARDS = ['AK', 'AQ', 'AJ', 'AT', 'KQ', 'KJ', 'KT', 'QJ',
              'QQ', 'JJ', 'TT', '99', '88', '77', '66', '55', '44', '33', '22']
CALL_CARD_SUITS = ['A9', 'A8', 'A7', 'A6', 'A5', 'A4', 'A3', 'A2',
                   'KJ', 'KT', 'QJ', 'QT', 'Q9', 'JT', 'J9', 'T9']

WIN_TITLE = "192.168.0.113 - 远程桌面连接"
DESKTOP_IMAGE = "desktop_image.jpg"
CROPPED_IMAGE = 'cropped_image.jpg'

# 截图偏移
OFFSET_X, OFFSET_Y = 0, 0
# 单个牌要截取的宽度和高度
CARD_WIDTH, CARD_HEIGHT = 38, 40

# 第1张手牌起始位置
CARD_ONE_POSITION = (653, 691)
# 第1张手牌花色位置
SUIT_ONE_POSITION = (676, 751)

# 第2张手牌起始位置
CARD_TWO_POSITION = (718, 690)
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

# 4种花色的颜色值
SPADE_COLOR = (0, 0, 0)
HEART_COLOR = (202, 23, 27)
CLUB_COLOR = (29, 126, 45)
DIAMOND_COLOR = (1, 30, 196)

# 表示需要读牌桌信息的位置及颜色值（出现手牌）
READ_FLAG_POSITION = (701, 724)
READ_FLAG_COLOR = (239, 239, 239)

# 按钮颜色
BUTTON_COLOR = (194, 79, 72)
BACKGROUND_COLOR = (34, 34, 34)

# 表示需要操作的位置及颜色值（出现弃牌按钮）
FOLD_BUTTON_POSITION = (937, 880)
CHECK_BUTTON_POSITION = (1096, 880)


# 需要远程到游戏桌面, 远程桌面分辩设置为：1440*900
# 游戏窗口最大化，牌需要设置为4色
# position=(x,y) 相对x为left,y为top
# region=(x,y,w,h)
# location=(region, position)


# 游戏窗口标题
WIN_TITLE = "192.168.0.113 - 远程桌面连接"
# 截图区域相对于左上角的偏移位
OFFSET_X, OFFSET_Y = 0, 0

# 牌
# 4种花色的颜色值。黑桃（Spade）红桃（Heart）梅花（Club）方块（Diamond）
SUIT_COLOR = ((0, 0, 0), (202, 23, 27), (29, 126, 45), (1, 30, 196))
# 单个牌要截取的宽度和高度
CARD_WIDTH, CARD_HEIGHT = 38, 40
# 第1张牌定位 (识别区域,花色位置)
CARD_1_LOCATION = ((653, 691, CARD_WIDTH, CARD_HEIGHT), (676, 751))
# 第2张牌定位 (识别区域,花色位置)
CARD_2_LOCATION = ((718, 690, CARD_WIDTH, CARD_HEIGHT), (737, 746))
# 第3张牌定位 (识别区域,花色位置)
CARD_3_LOCATION = ((488, 410, CARD_WIDTH, CARD_HEIGHT), (546, 486))
# 公共牌之间的间隔
PUB_CARD_SPACE_X = 100

# 底池
# 底池区域（l,t,w,h)
POOL_REGION = (729, 368, 88, 30)

# 判断
# 表示需要读牌桌信息的位置及颜色值（出现手牌）
READ_FLAG_POSITION = (701, 724)
READ_FLAG_COLOR = (239, 239, 239)

# 按钮颜色
BUTTON_COLOR = (194, 79, 72)
# 牌桌识别
TABLE_COLOR = (19, 90, 22)
TABLE_POSITION = (729, 627)
# 牌桌背景颜色
TABLE_BACKGROUND_COLOR = (34, 34, 34)


# 表示需要操作的位置及颜色值（出现弃牌按钮）
FOLD_BUTTON_POSITION = (937, 860)
CHECK_BUTTON_POSITION = (1096, 860)

# 操作
ACTION_CHECK_POSITION = (1052, 852)

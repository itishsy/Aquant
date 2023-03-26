# 合约类型常量
PRODUCT_EQUITY = u'股票'
PRODUCT_FUTURES = u'期货'
PRODUCT_OPTION = u'期权'
PRODUCT_INDEX = u'指数'
PRODUCT_COMBINATION = u'组合'
PRODUCT_FOREX = u'外汇'
PRODUCT_UNKNOWN = u'未知'
PRODUCT_SPOT = u'现货'

foodList = ['肠粉','糯米鸡','马蹄糕','双皮奶','鹌鹑蛋烧卖']

# 查询第5个元素 查询倒数第1个元素
print(foodList[4])
print(foodList[-1])

# 1.查询列表长度
Len = len(foodList)
print(Len)


foodList.append('艇仔粥')
print('# 2.列表操作：增加元素', foodList)

del foodList[2]
print('# 3.列表操作：删除元素 # 删除第3个元素', foodList)

foodList[0] = '豆浆'
print('# 4.列表操作：修改元素 # 修改第1个元素为’豆浆’', foodList)


print('# 1.访问前3个元素:',foodList[0:3])

print('# 2.简化版访问前3个元素', foodList[:3])

print('# 3.访问后3个元素', foodList[-3:])

'''
集合是一个无序不重复元素的序列.列表可以包括重复的元素，而集合是没有重复元素的容器，用花括号“{ }”来表示集合
'''

# 1.定义一个空的集合
BitcoinExchangeSets = set()

# 2.使用update来增加一个元素
BitcoinExchangeSets.update(['OKCOIN比特币交易所', '火币比特币交易所', 'LBANK比特币交易所'])
print(BitcoinExchangeSets)

# 3.使用discard来删除一个元素
BitcoinExchangeSets.discard('OKCOIN比特币交易所')
print(BitcoinExchangeSets)

# 4.使用in查询关键字
txBool = '火币比特币交易所' in BitcoinExchangeSets
print(txBool)

# 5修改集合内的元素
# 第一步，删除
BitcoinExchangeSets.discard('火币比特币交易所')
# 第二步，增加
BitcoinExchangeSets.update(['OKEX比特币交易所'])
print(BitcoinExchangeSets)


'''
字典是另一种可变容器模型，可存储任意类型的对象。字典的每个键值对“key=>value”用冒号“:”分隔，每个对之间用逗号“,”分隔，
整个字典包括在花括号“{ }”中，格式为d={key1 : value1, key2 : value2 }。
键必须是唯一的，且是不可变的，但值则不必唯一，可取任何数据类型，如字符串、数字或元组。
'''

# 创建新的字典
ExchangeDict={'中金所':'CFFEX',
			'上期所':'SHFE',
			'郑商所':'CZCE',
			'大商所':'DCE',
			'国际能源交易中心':'INE'}

# 1. 增加元素
ExchangeDict['上金所']=['SGE']
print(ExchangeDict)

# 2. 删除元素
del ExchangeDict['上金所']
print(ExchangeDict)

# 3. 查询元素，根据交易所名称查询交易所代码
print(ExchangeDict['中金所'])

# 4.修改元素
print('修改前，上期所代码：',ExchangeDict['上期所'])
ExchangeDict['上期所']=['SQS']
print('修改后，上期所代码：', ExchangeDict['上期所'])

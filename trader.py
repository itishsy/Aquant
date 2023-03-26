import backtrader as bt
import pandas as pd
import storage
from datetime import datetime
from strategy import macd

# 第一步 获取数据
start = datetime(2022, 3, 1)
end = datetime(2023, 3, 1)
k_data = storage.read('300059', beg=start, field='open,high,low,close,volume,datetime')
k_data.index = pd.to_datetime(k_data.datetime)
k_data['openinterest']=0
k_data.drop(['datetime'], axis=1, inplace=True)
# 最终需要的数据
data = bt.feeds.PandasData(dataname=k_data, fromdate=start, todate=end)

# 加载backtrader引擎
back_trader = bt.Cerebro()
# 将数据传入
back_trader.adddata(data)
# 策略加进来
back_trader.addstrategy(macd.Strategy)
#back_trader.broker.set_coc(True)
# 账户资金初始化
back_trader.broker.setcash(100000)
# 设置手续费
back_trader.broker.setcommission(commission=0.001)

# 输出初始数据
#d1 = start.strftime("%Y%M%D")
#d2 = end.strftime("%Y%M%D")
#print(f'初始化资金：{startCash}，回测时间：{d1}：{d2}')

# 开启回测
results = back_trader.run()
print('结果：%.2f'%back_trader.broker.getvalue())
#back_trader.plot(style='candlestick')
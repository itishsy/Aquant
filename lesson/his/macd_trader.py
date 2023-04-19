import backtrader as bt
import pandas as pd
import storage
from datetime import datetime

class Strategy(bt.Strategy):
    def log(self, txt, dt=None):
        dt = dt or self.datas[0].datetime.date(0)
        print('%s,%s' % (dt.isoformat(), txt))

    def __init__(self):
        # 指定价格序列
        self.close = self.datas[0].close
        # 交易定订单状态初始化
        self.order = None
        self.ema_1 = bt.indicators.ExponentialMovingAverage(self.close, period=12)
        self.ema_2 = bt.indicators.ExponentialMovingAverage(self.close, period=26)
        self.diff = self.ema_1 - self.ema_2
        self.dea = bt.indicators.ExponentialMovingAverage(self.diff, period=9)
        self.bar = (self.diff - self.dea) * 2

    def next(self):
        print(len(self.diff))

        if len(self.diff) > 1:
            self.log('{},{},{}'.format(self.diff[0], self.dea[0], self.bar[0]))

        # 检查持仓
        """if not self.position:
            if self.dea[0] > self.diff[0]:
                self.order = self.buy(size=5000)
        else:
            if self.dea[0] < self.diff[0]:
                self.order = self.sell(size=5000)"""

    def notify_order(self, order):
        """if order.status in [order.Submitted, order.Accepted]:
            if order.status in [order.Submitted]:
                self.log("提交订单……")
            if order.status in [order.Accepted]:
                self.log("接受订单……")
            return"""

        if order.status in [order.Completed]:
            if order.isbuy():
                self.log("buy: %.2f"%order.executed.price)
            if order.issell():
                self.log("sell: %.2f"%order.executed.price)

        #print("======================")
        self.order = None

# 第一步 获取数据
start = datetime(2010, 1, 1)
end = datetime.now()
k_data = storage.read('300059', klt=102, beg=start, field='open,high,low,close,volume,datetime')
k_data.index = pd.to_datetime(k_data.datetime)
k_data['openinterest']=0
k_data.drop(['datetime'],axis=1,inplace=True)

# 最终需要的数据
data = bt.feeds.PandasData(dataname=k_data, fromdate=start, todate=end)
# 加载backtrader引擎
back_trader = bt.Cerebro()
# 将数据传入
back_trader.adddata(data)
# 策略加进来
back_trader.addstrategy(Strategy)
# 以当日收盘价成交
back_trader.broker.set_coc(True)
# 账户资金初始化
back_trader.broker.setcash(100000)
# 设置手续费
back_trader.broker.setcommission(commission=0.001)
results = back_trader.run()
print('结果：%.2f'%back_trader.broker.getvalue())
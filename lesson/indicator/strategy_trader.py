import backtrader as bt
import pandas as pd
import storage
from datetime import datetime


class MAStrategy(bt.Strategy):
    def log(self, txt, dt = None):
        dt = dt or self.datas[0].datetime.date(0)
        print('%s,%s' % (dt.isoformat(), txt))

    def __init__(self):
        # 指定价格序列
        self.dataclose = self.datas[0].close
        # 交易定订单状态初始化
        self.order = None

        # 计算两条均线的值
        self.wma = bt.talib.WMA(self.dataclose, timeperiod=15)
        self.dema = bt.talib.DEMA(self.dataclose, timeperiod=15)

    def next(self):
        # 检查订单状态
        if self.order:
            print("等待成交")

        # 检查持仓
        if not self.position:
            # 没有持仓,买入开仓
            if self.dema[0] > self.wma[0]:
                # 快均线上穿慢均线
                self.order = self.buy(size=5000)
        else:
            # 手里有持仓，判断卖平
            if self.dema[0] < self.wma[0]:
                # 快均线下穿慢均线
                self.order = self.sell(size=5000)

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

        #self.log('订单完成！')
        #print("======================")
        self.order = None


class MACDStrategy(bt.Strategy):
    def log(self, txt, dt=None):
        dt = dt or self.datas[0].datetime.date(0)
        print('%s,%s' % (dt.isoformat(), txt))

    def __init__(self):
        # 指定价格序列
        self.dataclose = self.datas[0].close
        # 交易定订单状态初始化
        self.order = None
        self.ema_1 = bt.indicators.ExponentialMovingAverage(self.dataclose,period=12)
        self.ema_2 = bt.indicators.ExponentialMovingAverage(self.dataclose,period=26)
        self.diff = self.ema_1 - self.ema_2
        self.dea = bt.indicators.ExponentialMovingAverage(self.diff,period=9)
        self.macd = (self.diff - self.dea) * 2

    def next(self):
        # 检查订单状态
        if self.order:
            print("wait order")

        # 检查持仓
        if not self.position:
            if self.dea[0] > self.diff[0]:
                self.order = self.buy(size=5000)
        else:
            if self.dea[0] < self.diff[0]:
                self.order = self.sell(size=5000)

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

        #self.log('订单完成！')
        #print("======================")
        self.order = None

# 第一步 获取数据
start = datetime(2022, 3, 1)
end = datetime(2023, 3, 1)
k_data = storage.read('300059', beg=start, field='open,high,low,close,volume,datetime')
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
back_trader.addstrategy(MACDStrategy)
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
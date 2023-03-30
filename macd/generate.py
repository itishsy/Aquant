#from storage import kline
import talib as ta


def mark(stock_code):
    df = None # kline.read(stock_code)
    i = 0
    close = []
    for idx, row in df.iterrows():
        ema5 = ta.EMA(close, timeperiod=5)
        ema12 = ta.EMA(close, timeperiod=12)
        ema26 = ta.EMA(close, timeperiod=26)
        diff1 = ema5 - ema12
        diff2 = ema12 - ema26
        dea1 = ta.EMA(diff1, timeperiod=3)
        dea2 = ta.EMA(diff2, timeperiod=9)
        bar1 = diff1 - dea1
        bar2 = diff2 - dea2
        i += 1

close = [0,2]
ema12 = ta.EMA(close, timeperiod=12)
print(ema12)
from storage import fetch_data,upset
from strategy.macd import search
import pandas as pd

if __name__ == '__main__':
    stocks = ['510300']
    #fetch_data()
    #stocks = ['300842']
    #for code in stocks:
    #    upset(code)
    search(stocks=stocks, klt=102)
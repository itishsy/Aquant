from storage import fetch_data,upset
from strategy.macd import search

if __name__ == '__main__':
    fetch_data()
    stocks = ['510300', '512690', '512880']
    for code in stocks:
        upset(code)
    search(stocks=stocks, klt=102)
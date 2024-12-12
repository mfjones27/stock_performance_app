import yfinance as yf
import pandas as pd

def calculate_price_change(prev_close, current_price):
    return ((current_price - prev_close)/prev_close) * 100

def calculate_volume(volume):
    return volume / 1_000_000

def calculate_market_cap(market_cap):
    if len(str(market_cap)) > 12:
        mc = market_cap / 1_000_000_000_000
        value = 'Trillion'
        return mc, value
    elif len(str(market_cap)) > 9:
        mc = market_cap / 1_000_000_000
        value = 'Billion'
        return mc, value
    elif len(str(market_cap)) > 6:
        mc = market_cap / 1_000_000
        value = 'Million'
        return mc, value
    else:
        return market_cap, ''

def fetch_stock_data(ticker):
    stock_info = yf.Ticker(ticker).info

    stock_price_change = round(calculate_price_change(stock_info['regularMarketPreviousClose'], stock_info['currentPrice']), 2)
    volume = round(calculate_volume(stock_info['volume']), 2)
    market_cap, value = calculate_market_cap(stock_info['marketCap'])
    
    if stock_price_change > 0:
        sign = '+'
    elif stock_price_change < 0:
        sign = ''

    return {
        'name': stock_info['longName'],
        'ticker': stock_info['symbol'],
        'price': round(stock_info['currentPrice'], 2),
        'change': f'{sign}{stock_price_change}',
        'volume': f'{volume}M',
        'graph': '/static/images/sample-graph.png', # Fig, make graph.
        'metrics': [
            {'name': '52-Week High', 'value': f"{round(stock_info['fiftyTwoWeekHigh'], 2)}"},
            {'name': '52-Week Low', 'value': f"{round(stock_info['fiftyTwoWeekLow'], 2)}"},
            {'name': 'Market Cap', 'value': f"${round(market_cap, 1)} {value}"},
            {'name': 'PE Ratio', 'value': f'{round(stock_info['trailingPE'], 2)}'},
        ]
    }

def verify_ticker(ticker):
    try:
        data = yf.download(ticker, period='1d')
        if data.empty:
            return False
        else:
            return True
    except Exception as e:
        return False
    
def get_ohlc_data(ticker, date_range):
    if date_range == '1d':
        interval = '1m'
        data = yf.download(ticker, period=date_range, interval=interval)
    elif date_range == '5d':
        interval = '30m'
        data = yf.download(ticker, period=date_range, interval=interval)
        data.index = pd.to_datetime(data.index)
        data = data[~data.index.weekday.isin([5, 6])]
    else:
        data = yf.download(ticker, period=date_range)
    # Get OHLC data (Open, High, Low, Close)
    return data
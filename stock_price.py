import yfinance as yf
import matplotlib.pyplot as plt
import pandas as pd
from datetime import datetime, timedelta
import time
import requests

def fetch_stock_data_yf(ticker, days_back=30):
    """Fetch stock data using yfinance"""
    end_date = datetime.now()
    start_date = end_date - timedelta(days=days_back)
    
    for attempt in range(3):
        try:
            stock = yf.Ticker(ticker)
            df = stock.history(start=start_date, end=end_date)
            if not df.empty:
                # Convert timezone-aware index to naive
                df.index = df.index.tz_localize(None)
                return df
            print(f"Warning: Empty data frame for {ticker}")
        except Exception as e:
            print(f"yfinance attempt {attempt + 1} failed: {str(e)}")
            time.sleep(2)
    return None

def fetch_stock_data_manual(ticker, days_back=30):
    """Fallback method using direct Yahoo Finance query"""
    end_date = datetime.now()
    start_date = end_date - timedelta(days=days_back)
    
    try:
        period1 = int(start_date.timestamp())
        period2 = int(end_date.timestamp())
        
        url = f"https://query1.finance.yahoo.com/v7/finance/chart/{ticker}"
        params = {
            'range': f'{days_back}d',
            'interval': '1d',
            'includePrePost': 'false',
            'events': 'div,split'
        }
        
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
        
        response = requests.get(url, params=params, headers=headers)
        data = response.json()
        
        if 'chart' not in data or 'result' not in data['chart']:
            print("Invalid response structure")
            return None
            
        result = data['chart']['result'][0]
        timestamps = result['timestamp']
        close_prices = result['indicators']['quote'][0]['close']
        
        df = pd.DataFrame({
            'Date': pd.to_datetime(timestamps, unit='s'),
            'Close': close_prices
        })
        df.set_index('Date', inplace=True)
        return df
        
    except Exception as e:
        print(f"Manual fetch failed: {str(e)}")
        return None

def plot_stock_data(df, ticker):
    """Plot the stock price data"""
    plt.figure(figsize=(12, 6))
    # Convert both index and values to numpy arrays
    plt.plot(df.index.to_numpy(), df['Close'].to_numpy(), label='Closing Price', color='blue')
    plt.title(f'{ticker} Stock Price - Last 30 Days')
    plt.xlabel('Date')
    plt.ylabel('Price (USD)')
    plt.legend()
    plt.grid(True)
    plt.xticks(rotation=45)
    plt.tight_layout()
    plt.savefig(f'{ticker}_stock_price.png')
    plt.show()

def main():
    ticker_symbol = "AAPL"
    
    print(f"Attempting to fetch data for {ticker_symbol}...")
    
    stock_data = fetch_stock_data_yf(ticker_symbol)
    
    if stock_data is None:
        print("yfinance failed, attempting manual fetch...")
        stock_data = fetch_stock_data_manual(ticker_symbol)
    
    if stock_data is None:
        print("All fetch methods failed. Please:")
        print("- Update yfinance: pip install --upgrade yfinance")
        print("- Check internet connection")
        print("- Verify ticker symbol")
        return
        
    print("\nStock Data Preview:")
    print(stock_data[['Close']].head())
    plot_stock_data(stock_data, ticker_symbol)

if __name__ == "__main__":
    try:
        import yfinance
        print(f"yfinance version: {yfinance.__version__}")
        
        if yfinance.__version__ < "0.2":
            print("WARNING: yfinance version is old. Please update with:")
            print("pip install --upgrade yfinance")
        
        main()
    except ImportError:
        print("yfinance not installed. Install with: pip install yfinance")
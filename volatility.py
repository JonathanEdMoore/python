import yfinance as yf
import numpy as np

# Choose stock ticker symbol (e.g., 'AAPL' for Apple)
ticker = 'VT'

# Download historical data for the stock (adjusted close prices)
stock_data = yf.download(ticker, period="1y", interval="1d")  # 1 year of daily data

# Calculate daily returns
stock_data['Daily Returns'] = stock_data['Close'].pct_change()

# Calculate annualized standard deviation (volatility)
annual_volatility = np.std(stock_data['Daily Returns']) * np.sqrt(252)  # 252 trading days in a year

print(f"Annualized Volatility for {ticker}: {annual_volatility * 100:.2f}%")

import yfinance as yf
import pandas as pd
import numpy as np
import statsmodels.api as sm
import datetime

# Define the time range
start = datetime.datetime(1925, 1, 1)
end = datetime.datetime(2025, 3, 7)

# Take input for the stock ticker
stock_ticker = input("Enter the stock ticker (e.g., 'AAPL', 'MSFT', etc.): ").upper()

# Download data for the user-defined stock and VT using yfinance
tickers = [stock_ticker, 'VT']
data = yf.download(tickers, start=start, end=end)

# Access the 'Close' prices using multi-level columns
close_data = data['Close'].dropna(how="all")  # Drop rows where all tickers have NaN

# Calculate daily returns
returns = close_data.pct_change().dropna()

# Perform regression for the user-defined stock against VT
X = returns['VT']  # Independent variable (Benchmark ETF)
X = sm.add_constant(X)  # Adds a constant (alpha term) to the regression
y_stock = returns[stock_ticker]  # Dependent variable (User-defined stock)
model_stock = sm.OLS(y_stock, X).fit()

# Extract the beta (coefficient) from the model
beta_stock = model_stock.params.iloc[1]  # The second parameter is the beta

# Print the beta result
print(f"Beta of {stock_ticker} relative to VT: {beta_stock}")

# Loop through each ticker in the list
for ticker in tickers:
     # Download historical data for the stock (adjusted close prices)
    stock_data = yf.download(ticker, period="1y", interval="1d")  # 1 year of daily data

    # Calculate daily returns
    stock_data['Daily Returns'] = stock_data['Close'].pct_change()

    # Calculate annualized standard deviation (volatility)
    annual_volatility = np.std(stock_data['Daily Returns']) * np.sqrt(252)  # 252 trading days in a year

    if ticker == 'VT':
        vt_volatility = annual_volatility
    else :
        ticker_volatility = annual_volatility

    # Print the annualized volatility for the current ticker
    print(f"Annualized Volatility for {ticker}: {annual_volatility * 100:.2f}%")

# Calculate total risk, compensated risk, and uncompensated risk
compensated_risk = (beta_stock ** 2) * (vt_volatility ** 2)
total_risk = ticker_volatility ** 2
uncompensated_risk = total_risk - compensated_risk

print(f"\nTotal Risk of {stock_ticker}: {total_risk * 100:.2f}%")
print(f"\nCompensated Risk of {stock_ticker}: {compensated_risk * 100:.2f}%")
print(f"\nUncompensated Risk of {stock_ticker}: {uncompensated_risk * 100:.2f}%")

print(f"\n{compensated_risk / total_risk * 100:.2f}% of {stock_ticker}'s total risk is compensated.")
print(f"\n{uncompensated_risk / total_risk * 100:.2f}% of {stock_ticker}'s total risk is uncompensated.")
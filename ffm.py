import yfinance as yf
import pandas as pd
import numpy as np
import statsmodels.api as sm
import datetime

# Define the time range
start = datetime.datetime(2000, 1, 1)  # Adjusted for ETF data availability
end = datetime.datetime(2025, 3, 7)

# Take input for the stock ticker
stock_ticker = input("Enter the stock ticker (e.g., 'AAPL', 'MSFT', etc.): ").upper()

# Define ETFs for each factor
factor_etfs = {
    "Market (Mkt-RF)": "VT",    # Market ETF
    "Size (SMB)": "ACWI",        # Small-cap ETF
    "Value (HML)": "ACWV",      # Value ETF
    "Profitability (RMW)": "ACWI",  # Momentum ETF (proxy for profitability)
    "Investment (CMA)": "VTV"   # Value ETF (proxy for conservative investing)
}

# Add the user-defined stock to the list
tickers = [stock_ticker] + list(factor_etfs.values())

# Download adjusted close prices
data = yf.download(tickers, start=start, end=end)['Close'].dropna(how="all")

# Calculate daily returns
returns = data.pct_change().dropna()

# Define independent variables (factor ETFs as proxies)
factor_returns = returns[factor_etfs.values()]

# Perform multiple regression for the user-defined stock against the factor ETFs
X = sm.add_constant(factor_returns)  # Adds intercept (alpha)
y_stock = returns[stock_ticker]  # Dependent variable (stock excess return)
model = sm.OLS(y_stock, X).fit()

# Print regression summary
print(model.summary())

# Extract betas for each factor
factor_betas = model.params.iloc[1:]  # Ignore intercept
print("\nFactor Betas for", stock_ticker)
for factor, beta in zip(factor_etfs.keys(), factor_betas):
    print(f"{factor}: {beta:.4f}")


import yfinance as yf
import pandas as pd
import numpy as np
import statsmodels.api as sm
import datetime

# Define the time range
start = datetime.datetime(2020, 1, 1)
end = datetime.datetime(2025, 1, 1)

# Download data for VTI, VXUS, and VT using yfinance
tickers = ['VTI', 'VXUS', 'VT']
data = yf.download(tickers, start=start, end=end)

# Access the 'Close' prices using multi-level columns (auto_adjust=True, so Close is adjusted)
close_data = data['Close']

# Calculate daily returns
returns = close_data.pct_change().dropna()
print(returns.head())  # Print first few rows to check the data

# Perform regression for VTI against VT
X = returns['VT']  # Independent variable (Benchmark ETF)
X = sm.add_constant(X)  # Adds a constant (alpha term) to the regression
y_vti = returns['VTI']  # Dependent variable (VTI ETF)
model_vti = sm.OLS(y_vti, X).fit()

# Perform regression for VXUS against VT
y_vxus = returns['VXUS']  # Dependent variable (VXUS ETF)
model_vxus = sm.OLS(y_vxus, X).fit()

# Extract the betas (coefficients) from the models
beta_vti = model_vti.params[1]  # The second parameter is the beta
beta_vxus = model_vxus.params[1]

# Print the results
print(f"Beta of VTI relative to VT: {beta_vti}")
print(f"Beta of VXUS relative to VT: {beta_vxus}")

# Given data
return_vti = 0.0888  # VTI return (8.88%)

# Calculate the expected return of VXUS
expected_return_vxus = return_vti * (beta_vxus / beta_vti)

# Print the result
print(f"Expected Return of VXUS (based on market risk): {expected_return_vxus * 100:.2f}%")

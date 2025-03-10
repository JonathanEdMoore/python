import numpy as np
import pandas as pd
import scipy.optimize as sco
import statsmodels.api as sm
import yfinance as yf

# Step 1: Download historical price data for ETFs
tickers = ["VT", "AVUV", "AVDV"]
data = yf.download(tickers, start="2010-01-01", end="2025-01-01", auto_adjust=False)["Adj Close"]

# Check if data was downloaded properly
if data.isnull().all().all():
    raise ValueError("Error: No data downloaded for ETFs. Check ticker symbols or internet connection.")

# Compute daily returns
returns = data.pct_change().dropna()

# Step 2: Load Fama-French Five Factor data
ff5_url = "https://mba.tuck.dartmouth.edu/pages/faculty/ken.french/ftp/F-F_Research_Data_5_Factors_2x3_daily_CSV.zip"
ff5_factors = pd.read_csv(ff5_url, skiprows=3, index_col=0)

# Clean the dataset
ff5_factors = ff5_factors.iloc[:-1]  # Remove last row (non-data)
ff5_factors.index = pd.to_datetime(ff5_factors.index, format='%Y%m%d')  # Convert index to datetime
ff5_factors = ff5_factors / 100  # Convert from percentages to decimals

# Step 3: Ensure ETF returns only contain dates available in the Fama-French dataset
returns = returns.dropna()  # Drop NaNs in ETF returns
returns = returns.loc[returns.index.intersection(ff5_factors.index)]  # Align with Fama-French
ff5_factors = ff5_factors.loc[returns.index]  # Align Fama-French factors

# Step 4: Compute excess returns (ETF returns - risk-free rate)
rf = ff5_factors["RF"]
excess_returns = returns.sub(rf, axis=0)

# Drop missing excess returns before regression
excess_returns = excess_returns.dropna()

# Step 5: Estimate factor loadings (betas) for each ETF using OLS regression
betas = []
for ticker in tickers:
    X = ff5_factors[['Mkt-RF', 'SMB', 'HML', 'RMW', 'CMA']]
    X = sm.add_constant(X)  # Add intercept
    y = excess_returns[ticker]  # Excess returns of the ETF
    
    if y.isnull().all():
        print(f"Warning: {ticker} has no valid excess return data. Skipping regression.")
        betas.append(np.full(5, np.nan))  # Fill with NaNs if regression cannot run
        continue
    
    model = sm.OLS(y, X).fit()
    
    # Log factor betas
    print(f"\nFactor Betas for {ticker}:")
    print(model.params)
    
    betas.append(model.params[1:].values)  # Exclude the intercept

betas = np.array(betas)  # Convert list to NumPy array

# Step 6: Define estimated factor premiums (annualized)
factor_premiums = np.array([0.06, 0.025, 0.03, 0.035, 0.02])  # Assumed annualized premiums

# Compute expected returns for each ETF
expected_returns = betas @ factor_premiums  # Matrix multiplication

# Print expected returns
df_expected_returns = pd.DataFrame({"ETF": tickers, "Expected Return": expected_returns})
print("\nExpected Returns for Each ETF:")
print(df_expected_returns)

# Step 7: Compute Volatility (Standard Deviation) and Sharpe Ratio for Each Asset
sharpe_ratios = []
for ticker in tickers:
    # Compute annualized volatility
    volatility = returns[ticker].std() * np.sqrt(252)  # Annualize volatility (252 trading days)
    
    # Compute Sharpe Ratio
    sharpe_ratio = (expected_returns[tickers.index(ticker)] - 0.02) / volatility  # Assuming risk-free rate = 2%
    
    sharpe_ratios.append(sharpe_ratio)

# Print Sharpe Ratios for Each Asset
df_sharpe_ratios = pd.DataFrame({"ETF": tickers, "Sharpe Ratio": sharpe_ratios})
print("\nSharpe Ratios for Each ETF:")
print(df_sharpe_ratios)

# Define covariance matrix (Use historical daily returns)
cov_matrix = returns.cov().values  # Convert Pandas DataFrame to NumPy array

# Optimization function: Negative Sharpe Ratio (maximize Sharpe)
def neg_sharpe(weights, exp_returns, cov_matrix, risk_free_rate=0.02):
    port_return = np.dot(weights, exp_returns)
    port_volatility = np.sqrt(weights.T @ cov_matrix @ weights)
    sharpe_ratio = (port_return - risk_free_rate) / port_volatility
    return -sharpe_ratio  # Minimize negative Sharpe

# Constraints: Weights sum to 1
constraints = ({'type': 'eq', 'fun': lambda w: np.sum(w) - 1})
bounds = [(0, 1) for _ in range(len(expected_returns))]  # No short selling

# Initial Guess (Equal Weights)
init_guess = np.ones(len(expected_returns)) / len(expected_returns)

# Optimize Portfolio Weights
optimal = sco.minimize(neg_sharpe, init_guess, args=(expected_returns, cov_matrix),
                       method='SLSQP', constraints=constraints, bounds=bounds)

# Extract optimal weights
optimal_weights = optimal.x

# Display results
df_results = pd.DataFrame({"ETF": tickers, "Weight": optimal_weights})
print("\nOptimal Portfolio Weights:")
print(df_results)
import numpy as np
import pandas as pd
import datetime as dt
import yfinance as yf
import scipy.optimize as sc
import plotly.graph_objects as go

# Import data
def get_data(stocks, start, end):
    stock_data = yf.download(stocks, start=start, end=end, auto_adjust=True)["Close"]
    returns = stock_data.pct_change()
    mean_returns = returns.mean()
    cov_matrix = returns.cov()
    return mean_returns, cov_matrix

def portfolio_performance(weights, mean_returns, cov_matrix):
    adjusted_returns = np.sum(mean_returns * weights) * 252
    std = np.sqrt(np.dot(weights.T, np.dot(cov_matrix, weights))) * np.sqrt(252)
    return adjusted_returns, std

def negative_sr(weights, mean_returns, cov_matrix, risk_free_rate=0):
    p_returns, p_std = portfolio_performance(weights, mean_returns, cov_matrix)
    return -(p_returns - risk_free_rate) / p_std

def max_sr(mean_returns, cov_matrix, risk_free_rate=0, constraint_set=(0, 1)):
    num_assets = len(mean_returns)
    args = (mean_returns, cov_matrix, risk_free_rate)
    constraints = ({'type': 'eq', 'fun': lambda x: np.sum(x) - 1})
    bounds = tuple(constraint_set for _ in range(num_assets))
    result = sc.minimize(negative_sr, num_assets * [1. / num_assets], args=args,
                         method='SLSQP', bounds=bounds, constraints=constraints)
    return result

def calculated_results(mean_returns, cov_matrix, risk_free_rate=0):
    max_sr_portfolio = max_sr(mean_returns, cov_matrix, risk_free_rate)
    max_sr_returns, max_sr_std = portfolio_performance(max_sr_portfolio['x'], mean_returns, cov_matrix)

    print("Tangency Portfolio Weights (Maximum Sharpe Ratio Portfolio):")
    for stock, weight in zip(mean_returns.index, max_sr_portfolio['x']):
        print(f"{stock}: {weight:.4f}")
    
    print(f"\nAnnualized Return of the Tangency Portfolio: {max_sr_returns * 100:.2f}%")
    print(f"Annualized Volatility of the Tangency Portfolio: {max_sr_std * 100:.2f}%")
    return max_sr_returns, max_sr_std

def ef_graph(mean_returns, cov_matrix, risk_free_rate=0.0462):
    max_sr_returns, max_sr_std = calculated_results(mean_returns, cov_matrix, risk_free_rate)

    manual_weights = np.array([float(w) for w in input("Enter the portfolio weights (comma separated, e.g., '0.6,0.4'): ").split(',')])
    manual_return, manual_volatility = portfolio_performance(manual_weights, mean_returns, cov_matrix)
    
    print("\nManually Defined Portfolio:")
    print(f"Annualized Return: {manual_return * 100:.2f}%")
    print(f"Annualized Volatility: {manual_volatility * 100:.2f}%")
    return max_sr_returns, max_sr_std, manual_return, manual_volatility

stock_list = input("Enter the stock tickers (e.g., 'AAPL', 'MSFT', etc.): ").upper().split(',')
end_date_str = dt.datetime.now().strftime('%Y-%m-%d')
start_date_str = '2007-04-03'

mean_returns, cov_matrix = get_data(stock_list, start=start_date_str, end=end_date_str)
ef_graph(mean_returns, cov_matrix)

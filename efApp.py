import numpy as np
import pandas as pd
import datetime
import yfinance as yf
import scipy.optimize as sc
import plotly.graph_objects as go

# Import data
def get_data(stocks, start, end):
    # Download the adjusted closing price data
    stock_data = yf.download(stocks, start=start, end=end, auto_adjust=True)["Close"].dropna(how="all")
    
    # Ensure stock_data index is timezone-naive
    stock_data.index = stock_data.index.tz_localize(None)
    
    # Calculate daily returns
    returns = stock_data.pct_change()
    
    # Add dividend to returns for specific stocks
    bond_funds = ["BND", "BNDW", "AGG", "TLT"]
    for ticker in bond_funds:
        if ticker in stocks:
            stock = yf.Ticker(ticker)
            dividends = stock.dividends  # Get dividends for the specified date range
            
            # Ensure dividend data index is timezone-naive
            dividends.index = dividends.index.tz_localize(None)

            # Iterate through stock_data.index and add dividend where dates match
            for date in stock_data.index:
                if date in dividends.index:
                    # Get the dividend for the date and add it to the return
                    dividend = dividends.loc[date]
                    returns.loc[date, ticker] += dividend / stock_data.loc[date, ticker]  # Add dividend yield to return
            
    # Calculate mean returns and covariance matrix
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

def portfolio_variance(weights, mean_returns, cov_matrix):
    return portfolio_performance(weights, mean_returns, cov_matrix)[1]

def minimize_variance(mean_returns, cov_matrix, constraint_set=(0,1)):
    "Minimize the portfolio variance by altering the weights/allocation of assets in the portfolio"
    num_assets = len(mean_returns)
    args = (mean_returns, cov_matrix)
    constraints = ({'type': 'eq', 'fun': lambda x: np.sum(x) - 1})
    bound = constraint_set
    bounds = tuple(bound for asset in range(num_assets))
    result = sc.minimize(portfolio_variance, num_assets * [1. / num_assets], args=args,
                         method='SLSQP', bounds=bounds, constraints=constraints)
    
    return result

def portfolio_return(weights, mean_returns, cov_matrix):
    return portfolio_performance(weights, mean_returns, cov_matrix)[0]

def efficient_opt(mean_returns, cov_matrix, return_target, constraint_set=(0,1)):
    """For each returnTarget, we want to optimize the portfolio for min variance"""
    num_assets = len(mean_returns)
    args = (mean_returns, cov_matrix)

    constraints = ({'type': 'eq', 'fun': lambda x: portfolio_return(x, mean_returns, cov_matrix) - return_target},
                   {'type': 'eq', 'fun': lambda x: np.sum(x) - 1})
    bound = constraint_set
    bounds = tuple(bound for asset in range(num_assets))
    eff_opt = sc.minimize(portfolio_variance, num_assets * [1. / num_assets], args=args,
                         method='SLSQP', bounds=bounds, constraints=constraints)

    return eff_opt

def calculated_results(mean_returns, cov_matrix, risk_free_rate=0):
    max_sr_portfolio = max_sr(mean_returns, cov_matrix, risk_free_rate)
    max_sr_returns, max_sr_std = portfolio_performance(max_sr_portfolio['x'], mean_returns, cov_matrix)
    max_sr_allocation = pd.DataFrame(max_sr_portfolio['x'], index=mean_returns.index, columns=['allocation'])
    max_sr_allocation.allocation = [round(1 * 100, 0) for i in max_sr_allocation.allocation]

    # Calculate Sharpe Ratio
    max_sr_sharpe = (max_sr_returns - risk_free_rate) / max_sr_std

    #Print the weights of the tangency portfolio
    print("Tangency Portfolio Weights (Maximum Sharpe Ratio Portfolio):")
    for stock, weight in zip(mean_returns.index, max_sr_portfolio['x']):
        print(f"{stock}: {weight:.4f}")
    
    # Print the annualized returns, annualized volatility, and Sharpe Ratio as percentages
    print(f"\nAnnualized Return of the Tangency Portfolio: {max_sr_returns * 100:.2f}%")
    print(f"Annualized Volatility of the Tangency Portfolio: {max_sr_std * 100:.2f}%")
    print(f"Sharpe Ratio of the Tangency Portfolio: {max_sr_sharpe:.4f}\n")

    # Min Volatility Portfolio
    min_vol_portfolio = minimize_variance(mean_returns, cov_matrix)
    min_vol_returns, min_vol_std = portfolio_performance(min_vol_portfolio['x'], mean_returns, cov_matrix)
    min_vol_allocation = pd.DataFrame(min_vol_portfolio['x'], index=mean_returns.index, columns=['allocation'])
    min_vol_allocation.allocation = [round(i * 100, 0) for i in min_vol_allocation.allocation]

    # Efficient Frontier
    efficient_list = []
    target_returns = np.linspace(min_vol_returns, max_sr_returns, 20)
    for target in target_returns:
        efficient_list.append(efficient_opt(mean_returns, cov_matrix, target)['fun'])

    max_sr_returns, max_sr_std = round(max_sr_returns * 100, 2), round(max_sr_std * 100, 2)
    min_vol_returns, min_vol_std = round(min_vol_returns * 100, 2), round(min_vol_std * 100, 2)

    return max_sr_returns, max_sr_std, min_vol_returns, min_vol_std, efficient_list, target_returns

def ef_graph(mean_returns, cov_matrix, risk_free_rate=0.0462):
    max_sr_returns, max_sr_std, min_vol_returns, min_vol_std, efficient_list, target_returns = calculated_results(mean_returns, cov_matrix, risk_free_rate)

    manual_weights = np.array([float(w) for w in input("Enter the portfolio weights (comma separated, e.g., '0.6,0.4'): ").split(',')])
    manual_return, manual_volatility = portfolio_performance(manual_weights, mean_returns, cov_matrix)

    manual_sharpe = (manual_return - risk_free_rate) / manual_volatility

    
    print("\nManually Defined Portfolio:")
    print(f"Annualized Return: {manual_return * 100:.2f}%")
    print(f"Annualized Volatility: {manual_volatility * 100:.2f}%")
    print(f"Sharpe Ratio of the Manually Defined Portfolio: {manual_sharpe:.4f}\n")
    
    tangency_portfolio = go.Scatter(
        name='Tangency Portfolio',
        mode='markers',
        x=[max_sr_std],
        y=[max_sr_returns],
        marker=dict(color='red', size=14, line=dict(width=3, color='black'))
    )

     # Min Vol
    min_vol = go.Scatter(
        name='Minimum Volatility',
        mode='markers',
        x=[min_vol_std],
        y=[min_vol_returns],
        marker=dict(color='green', size=14, line=dict(width=3, color='black'))
    )

    # Efficient Frontier
    ef_curve = go.Scatter(
        name='Efficient Frontier',
        mode='lines',
        x=[round(ef_std * 100, 2) for ef_std in efficient_list],
        y=[round(target * 100, 2) for target in target_returns],
        line=dict(color='black', width=4, dash='dashdot')
    )

    # Tangency Line (Capital Market Line)
    CML_x = np.linspace(0, 100, 500)  # Adjusted to extend the CML
    CML_y = risk_free_rate * 100 + (max_sr_returns - risk_free_rate * 100) / max_sr_std* CML_x
    CML = go.Scatter(
        name='Capital Market Line (CML)',
        mode='lines',
        x=CML_x,
        y=CML_y,
        line=dict(color='blue', width=2, dash='dash')
    )

    x_max = max_sr_std* 1.25
    y_max = max_sr_returns * 1.25

    data = [ef_curve, CML, min_vol, tangency_portfolio]

    layout = go.Layout(
        title='Portfolio Optimization with the Efficient Frontier',
        yaxis=dict(title='Annualized Return (%)', range=[0, y_max]),
        xaxis=dict(title='Annualized Volatility (%)', range=[0, x_max]),
        showlegend=True,
        legend=dict(
            x=0.75, y=0, traceorder='normal',
            bgcolor='#E2E2E2',
            bordercolor='black',
            borderwidth=2),
        width=1250,
        height=1250
    )

    fig = go.Figure(data=data, layout=layout)
    return fig.show()

stock_list = input("Enter the stock tickers (e.g., 'AAPL', 'MSFT', etc.): ").upper().split(',')
start_date_str = datetime.datetime(1925, 1, 1)
end_date_str = datetime.datetime(2025, 3, 19)

mean_returns, cov_matrix = get_data(stock_list, start=start_date_str, end=end_date_str)
ef_graph(mean_returns, cov_matrix)

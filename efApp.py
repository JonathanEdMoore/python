import numpy as np
import pandas as pd
import datetime as dt
import yfinance as yf
import scipy.optimize as sc
import plotly.graph_objects as go

# Import data
def get_data(stocks, start, end):
    stock_data = yf.download(stocks, start=start, end=end)
    stock_data = stock_data['Close']

    returns = stock_data.pct_change()
    meanReturns = returns.mean()
    covMatrix = returns.cov()

    return meanReturns, covMatrix

def average_annual_dividend_yield(tickers):
    yields = {}
    
    for ticker in tickers:
        # Fetch the stock data
        stock = yf.Ticker(ticker)
        
        # Get the historical dividends
        dividends = stock.dividends
        
        if dividends.empty:
            yields[ticker] = 0  # No dividends paid
            continue
        
        # Get historical price data (close prices)
        price_data = stock.history(period="max")
        
        # Calculate the annual dividends
        annual_dividends = dividends.groupby(dividends.index.year).sum()
        
        # Calculate the average annual closing price
        annual_prices = price_data['Close'].resample('YE').mean()
        
        # Ensure the years match between dividends and prices
        annual_dividends = annual_dividends[annual_dividends.index.isin(annual_prices.index.year)]
        annual_prices = annual_prices[annual_prices.index.year.isin(annual_dividends.index)]
        
        # Calculate the annual dividend yield
        annual_yields = (annual_dividends / annual_prices.values)
        
        # Calculate the average annual dividend yield
        average_annual_yield = annual_yields.mean()
        
        # Store the result in the dictionary
        yields[ticker] = average_annual_yield
    
    # Convert the dictionary to a Pandas Series
    return pd.Series(yields).sort_index()

def portfolioPerformance(weights, meanReturns, covMatrix, dividendYields, riskFreeRate=0):
    # Calculate the weighted average dividend yield
    weighted_dividends = np.sum(weights * dividendYields)
    
    # Calculate the weighted average return (annualized return)
    adjusted_returns = np.sum(meanReturns * weights) * 252 + weighted_dividends
    
    # Calculate the standard deviation (volatility)
    std = np.sqrt(np.dot(weights.T, np.dot(covMatrix, weights))) * np.sqrt(252)
    return adjusted_returns, std

def negativeSR(weights, meanReturns, covMatrix, dividendYields, riskFreeRate=0):
    pReturns, pStd = portfolioPerformance(weights, meanReturns, covMatrix, dividendYields, riskFreeRate)
    return -(pReturns - riskFreeRate) / pStd

def maxSR(meanReturns, covMatrix, dividendYields, riskFreeRate=0, constraintSet=(0, 1)):
    numAssets = len(meanReturns)
    args = (meanReturns, covMatrix, dividendYields, riskFreeRate)
    constraints = ({'type': 'eq', 'fun': lambda x: np.sum(x) - 1})
    bound = constraintSet
    bounds = tuple(bound for asset in range(numAssets))
    result = sc.minimize(negativeSR, numAssets * [1. / numAssets], args=args,
                         method='SLSQP', bounds=bounds, constraints=constraints)
    return result

def portfolioReturn(weights, meanReturns, covMatrix, dividendYields):
    return portfolioPerformance(weights, meanReturns, covMatrix, dividendYields)[0]

def calculatedResults(meanReturns, covMatrix, dividendYields, riskFreeRate=0, borrowingRate=0, constraintSet=(0, 1)):
    # Max Sharpe Ratio Portfolio
    maxSR_Portfolio = maxSR(meanReturns, covMatrix, dividendYields, riskFreeRate)
    maxSR_returns, maxSR_std = portfolioPerformance(maxSR_Portfolio['x'], meanReturns, covMatrix, dividendYields, riskFreeRate)

    # Print the weights of the tangency portfolio
    print("Tangency Portfolio Weights (Maximum Sharpe Ratio Portfolio):")
    for stock, weight in zip(meanReturns.index, maxSR_Portfolio['x']):
        print(f"{stock}: {weight:.4f}")

    # Print the annualized returns, annualized volatility, and Sharpe Ratio as percentages
    print(f"\nAnnualized Return of the Tangency Portfolio: {maxSR_returns * 100:.2f}%")
    print(f"Annualized Volatility of the Tangency Portfolio: {maxSR_std * 100:.2f}%")

    return maxSR_returns, maxSR_std

def EF_graph(meanReturns, covMatrix, dividendYields, riskFreeRate=0.0462, borrowingRate=0.0, constraintSet=(0, 1)):
    maxSR_returns, maxSR_std = calculatedResults(meanReturns, covMatrix, dividendYields, riskFreeRate, borrowingRate, constraintSet)

    # Input manually defined portfolio weights (user-defined)
    manual_weights = input("Enter the portfolio weights (comma separated, e.g., '0.6,0.4'): ").split(',')
    manual_weights = np.array([float(w) for w in manual_weights])  # Convert to numpy array

    # Calculate annualized return and volatility for the manually defined portfolio
    manual_return, manual_volatility = portfolioPerformance(manual_weights, meanReturns, covMatrix, dividendYields)

    # Print the results for the manually defined portfolio
    print(f"\nManually Defined Portfolio:")
    print(f"Annualized Return: {manual_return * 100:.2f}%")
    print(f"Annualized Volatility: {manual_volatility * 100:.2f}%")

    return maxSR_returns, maxSR_std, manual_return, manual_volatility

# Start of the main program
stock_list = input("Enter the stock tickers (e.g., 'AAPL', 'MSFT', etc.): ").upper().split(',')
stocks = [stock for stock in stock_list]

end_date = dt.datetime.now()
end_date_str = end_date.strftime('%Y-%m-%d')
start_date_str = '2007-04-03'

meanReturns, covMatrix = get_data(stocks, start=start_date_str, end=end_date_str)

dividendYields = average_annual_dividend_yield(stocks)

EF_graph(meanReturns, covMatrix, dividendYields)

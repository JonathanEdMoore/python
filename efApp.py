import numpy as np
import pandas as pd
import datetime as dt
import yfinance as yf
import scipy.optimize as sc
import plotly.graph_objects as go

# Import data
def get_data(stocks, start, end):
    stock_data = yf.download(stocks, start=start, end=end)
    stock_data = stock_data['Adj Close']

    returns = stock_data.pct_change()
    meanReturns = returns.mean()
    covMatrix = returns.cov()

    return meanReturns, covMatrix

def get_dividend_yield(tickers, period):
    dividend_yields = {}

    for ticker in tickers:
        # Fetch historical data for the stock
        stock = yf.Ticker(ticker)
        data = stock.history(period=period)

        # Resample dividend data to get annual dividends
        dividends = stock.dividends
        annual_dividends = dividends.resample('YE').sum()  # Sum dividends per year

        # Calculate average closing price per year
        annual_prices = data['Close'].resample('YE').mean()

        # Calculate annual dividend yields
        annual_dividend_yields = annual_dividends / annual_prices

        # Average annual dividend yield
        average_dividend_yield = annual_dividend_yields.mean()

        # Store the result in the dictionary
        dividend_yields[ticker] = average_dividend_yield

    # Convert dictionary to Pandas Series
    dividend_yield_series = pd.Series(dividend_yields, name='Dividend Yield')

    dividend_yield_series.name = "Ticker"  # Set the name of the Series
    
    return dividend_yield_series

def portfolioPerformance(weights, meanReturns, covMatrix, riskFreeRate=0, leverageCost=0):
    # Determine if leverage is used
    leverage = np.sum(weights) - 1
    # Apply leverage cost to the leveraged portion of the portfolio
    if leverage > 0:
        adjusted_returns = np.sum(meanReturns * weights) * 252 - leverage * leverageCost
    else:
        adjusted_returns = np.sum(meanReturns * weights) * 252
    
    std = np.sqrt(np.dot(weights.T, np.dot(covMatrix, weights))) * np.sqrt(252)
    return adjusted_returns, std

def negativeSR(weights, meanReturns, covMatrix, riskFreeRate=0, leverageCost=0):
    pReturns, pStd = portfolioPerformance(weights, meanReturns, covMatrix, riskFreeRate, leverageCost)
    return -(pReturns - riskFreeRate) / pStd

def maxSR(meanReturns, covMatrix, riskFreeRate=0, leverageCost=0, constraintSet=(0, 1)):
    "Minimize the negative SR, by altering the weights of the portfolio"
    numAssets = len(meanReturns)
    args = (meanReturns, covMatrix, riskFreeRate, leverageCost)
    constraints = ({'type': 'eq', 'fun': lambda x: np.sum(x) - 1})
    bound = constraintSet
    bounds = tuple(bound for asset in range(numAssets))
    result = sc.minimize(negativeSR, numAssets * [1. / numAssets], args=args,
                         method='SLSQP', bounds=bounds, constraints=constraints)
    return result

def portfolioVariance(weights, meanReturns, covMatrix):
    return portfolioPerformance(weights, meanReturns, covMatrix)[1]

def minimizeVariance(meanReturns, covMatrix, constraintSet=(0, 1)):
    "Minimize the portfolio variance by altering the weights/allocation of assets in the portfolio"
    numAssets = len(meanReturns)
    args = (meanReturns, covMatrix)
    constraints = ({'type': 'eq', 'fun': lambda x: np.sum(x) - 1})
    bound = constraintSet
    bounds = tuple(bound for asset in range(numAssets))
    result = sc.minimize(portfolioVariance, numAssets * [1. / numAssets], args=args,
                         method='SLSQP', bounds=bounds, constraints=constraints)
    return result

def portfolioReturn(weights, meanReturns, covMatrix):
    return portfolioPerformance(weights, meanReturns, covMatrix)[0]

def efficientOpt(meanReturns, covMatrix, returnTarget, constraintSet=(0, 1)):
    """For each returnTarget, we want to optimize the portfolio for min variance"""
    numAssets = len(meanReturns)
    args = (meanReturns, covMatrix)

    constraints = ({'type': 'eq', 'fun': lambda x: portfolioReturn(x, meanReturns, covMatrix) - returnTarget},
                   {'type': 'eq', 'fun': lambda x: np.sum(x) - 1})
    bound = constraintSet
    bounds = tuple(bound for asset in range(numAssets))
    effOpt = sc.minimize(portfolioVariance, numAssets * [1. / numAssets], args=args,
                         method='SLSQP', bounds=bounds, constraints=constraints)

    return effOpt

def calculatedResults(meanReturns, covMatrix, riskFreeRate=0, leverageCost=0, constraintSet=(0, 1)):
    """Read in mean, cov matrix, and other financial information
       Output, Max SR, Min Volatility, efficient frontier """
    # Max Sharpe Ratio Portfolio
    maxSR_Portfolio = maxSR(meanReturns, covMatrix, riskFreeRate, leverageCost)
    maxSR_returns, maxSR_std = portfolioPerformance(maxSR_Portfolio['x'], meanReturns, covMatrix, riskFreeRate, leverageCost)
    maxSR_allocation = pd.DataFrame(maxSR_Portfolio['x'], index=meanReturns.index, columns=['allocation'])
    maxSR_allocation.allocation = [round(i * 100, 0) for i in maxSR_allocation.allocation]

    # Calculate Sharpe Ratio
    maxSR_sharpe = (maxSR_returns - riskFreeRate) / maxSR_std

    # Print the weights of the tangency portfolio
    print("Tangency Portfolio Weights (Maximum Sharpe Ratio Portfolio):")
    for stock, weight in zip(meanReturns.index, maxSR_Portfolio['x']):
        print(f"{stock}: {weight:.4f}")

    # Print the annualized returns, annualized volatility, and Sharpe Ratio as percentages
    print(f"\nAnnualized Return of the Tangency Portfolio: {maxSR_returns * 100:.2f}%")
    print(f"Annualized Volatility of the Tangency Portfolio: {maxSR_std * 100:.2f}%")
    print(f"Sharpe Ratio of the Tangency Portfolio: {maxSR_sharpe:.4f}\n")

    # Min Volatility Portfolio
    minVol_Portfolio = minimizeVariance(meanReturns, covMatrix)
    minVol_returns, minVol_std = portfolioPerformance(minVol_Portfolio['x'], meanReturns, covMatrix, riskFreeRate, leverageCost)
    minVol_allocation = pd.DataFrame(minVol_Portfolio['x'], index=meanReturns.index, columns=['allocation'])
    minVol_allocation.allocation = [round(i * 100, 0) for i in minVol_allocation.allocation]

    # Efficient Frontier
    efficientList = []
    targetReturns = np.linspace(minVol_returns, maxSR_returns, 20)
    for target in targetReturns:
        efficientList.append(efficientOpt(meanReturns, covMatrix, target)['fun'])

    maxSR_returns, maxSR_std = round(maxSR_returns * 100, 2), round(maxSR_std * 100, 2)
    minVol_returns, minVol_std = round(minVol_returns * 100, 2), round(minVol_std * 100, 2)

    return maxSR_returns, maxSR_std, minVol_returns, minVol_std, efficientList, targetReturns

def EF_graph(meanReturns, covMatrix, riskFreeRate=0.0242, leverageCost=0.0, constraintSet=(0, 1)):
    """Return a graph plotting the min vol, max sr, efficient frontier, and tangency line"""
    maxSR_returns, maxSR_std, minVol_returns, minVol_std, efficientList, targetReturns = calculatedResults(meanReturns, covMatrix, riskFreeRate, leverageCost, constraintSet)

    # Tangency Porfolio
    TangencyPortfolio = go.Scatter(
        name='Tangency Portfolio',
        mode='markers',
        x=[maxSR_std],
        y=[maxSR_returns],
        marker=dict(color='red', size=14, line=dict(width=3, color='black'))
    )

    # Min Vol
    MinVol = go.Scatter(
        name='Minimum Volatility',
        mode='markers',
        x=[minVol_std],
        y=[minVol_returns],
        marker=dict(color='green', size=14, line=dict(width=3, color='black'))
    )

    # Efficient Frontier
    EF_curve = go.Scatter(
        name='Efficient Frontier',
        mode='lines',
        x=[round(ef_std * 100, 2) for ef_std in efficientList],
        y=[round(target * 100, 2) for target in targetReturns],
        line=dict(color='black', width=4, dash='dashdot')
    )

    # Tangency Line (Capital Market Line)
    CML_x = np.linspace(0, 100, 500)  # Adjusted to extend the CML
    CML_y = riskFreeRate * 100 + (maxSR_returns - riskFreeRate * 100) / maxSR_std * CML_x
    CML = go.Scatter(
        name='Capital Market Line (CML)',
        mode='lines',
        x=CML_x,
        y=CML_y,
        line=dict(color='blue', width=2, dash='dash')
    )

    x_max = maxSR_std * 1.25
    y_max = maxSR_returns * 1.25

    data = [EF_curve, CML, MinVol, TangencyPortfolio]

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

stock_list = ['VT', 'BNDW']
stocks = [stock for stock in stock_list]

end_date = dt.datetime.now()

end_date_str = end_date.strftime('%Y-%m-%d')
start_date_str = '2007-04-03'

meanReturns, covMatrix = get_data(stocks, start=start_date_str, end=end_date_str)

EF_graph(meanReturns, covMatrix)
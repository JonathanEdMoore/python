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

stock_list = ['VT', 'BND']
stocks = [stock for stock in stock_list]

end_date = dt.datetime.now()

end_date_str = end_date.strftime('%Y-%m-%d')
start_date_str = '2007-04-03'

meanReturns, covMatrix = get_data(stocks, start=start_date_str, end=end_date_str)

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

def calculateTargetPortfolio_v(meanReturns, covMatrix, targetVolatility, cmlReturn, constraintSet=(0, 1)):
    numAssets = len(meanReturns)
    args = (meanReturns, covMatrix)

    constraints = ({'type': 'eq', 'fun': lambda x: portfolioPerformance(x, meanReturns, covMatrix)[1] - targetVolatility},
                   {'type': 'eq', 'fun': lambda x: portfolioReturn(x, meanReturns, covMatrix) - cmlReturn})
    
    bound = constraintSet
    bounds = tuple(bound for asset in range(numAssets))
    result = sc.minimize(portfolioVariance, numAssets * [1. / numAssets], args=args,
                         method='SLSQP', bounds=bounds, constraints=constraints)
    return result

def calculateTargetPortfolio_r(meanReturns, covMatrix, targetReturns, cmlVolatility, constraintSet=(0, 1)):
    numAssets = len(meanReturns)
    args = (meanReturns, covMatrix)

    constraints = ({'type': 'eq', 'fun': lambda x: portfolioPerformance(x, meanReturns, covMatrix)[0] - targetReturns},
                   {'type': 'eq', 'fun': lambda x: portfolioVariance(x, meanReturns, covMatrix) - cmlVolatility})
    
    bound = constraintSet
    bounds = tuple(bound for asset in range(numAssets))
    result = sc.minimize(portfolioVariance, numAssets * [1. / numAssets], args=args,
                         method='SLSQP', bounds=bounds, constraints=constraints)
    return result

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

    def calculate_single_stock_volatility(stock, meanReturns, covMatrix):
        weights = np.zeros(len(meanReturns))
        weights[meanReturns.index.get_loc(stock)] = 1
        return portfolioPerformance(weights, meanReturns, covMatrix, riskFreeRate, leverageCost)[1]
    
    def calculate_single_stock_return(stock, meanReturns):
        return meanReturns[stock] * 252  # Annualize the return
    # 100% VT Portfolio
    vt_volatility = calculate_single_stock_volatility('VT', meanReturns, covMatrix)
    vt_return = calculate_single_stock_return('VT', meanReturns)
    vt_sharpe = (vt_return - riskFreeRate) / vt_volatility

    # 100% BND Portfolio
    bnd_volatility = calculate_single_stock_volatility('BND', meanReturns, covMatrix)
    bnd_return = calculate_single_stock_return('BND', meanReturns)
    bnd_sharpe = (bnd_return - riskFreeRate) / bnd_volatility

    print("Portfolio Weights for 100% VT")
    for stock, weight in zip(meanReturns.index, [0, 1]):
        print(f"{stock}: {weight:.4f}")
    
    print(f"\nAnnualized Return of the VT Portfolio: {vt_return * 100:.2f}%")
    print(f"Annualized Volatility of the VT Porfolio: {vt_volatility * 100:.2f}%")
    print(f"Sharpe Ratio of the VT Portfolio: {vt_sharpe:.4f}\n")

    print("Portfolio Weights for 100% BND")
    for stock, weight in zip(meanReturns.index, [1, 0]):
        print(f"{stock}: {weight:.4f}")
    
    print(f"\nAnnualized Return of the BND Portfolio: {bnd_return * 100:.2f}%")
    print(f"Annualized Volatility of the BND Portfolio: {bnd_volatility * 100:.2f}%")
    print(f"Sharpe Ratio of the BND Portfolio: {bnd_sharpe:.4f}\n")

    # Min Volatility Portfolio
    minVol_Portfolio = minimizeVariance(meanReturns, covMatrix)
    minVol_returns, minVol_std = portfolioPerformance(minVol_Portfolio['x'], meanReturns, covMatrix, riskFreeRate, leverageCost)
    minVol_allocation = pd.DataFrame(minVol_Portfolio['x'], index=meanReturns.index, columns=['allocation'])
    minVol_allocation.allocation = [round(i * 100, 0) for i in minVol_allocation.allocation]

    # Efficient Frontier
    efficientList = []
    targetReturns = np.linspace(bnd_return, vt_return, 20)
    for target in targetReturns:
        efficientList.append(efficientOpt(meanReturns, covMatrix, target)['fun'])
    
    cml_return = (maxSR_sharpe * vt_volatility) + riskFreeRate
    cml_volatility = (vt_return - riskFreeRate) / maxSR_sharpe

    targetPortfolio_v = calculateTargetPortfolio_v(meanReturns, covMatrix, vt_volatility, cml_return, constraintSet)
    target_returns_v, target_std_v = portfolioPerformance(targetPortfolio_v['x'], meanReturns, covMatrix, riskFreeRate, leverageCost)
    target_sharpe_v = (target_returns_v - riskFreeRate) / target_std_v
    target_weights_v = pd.DataFrame(targetPortfolio_v['x'], index=meanReturns.index, columns=['allocation'])
    target_weights_v.allocation = [round(i * 100, 2) for i in target_weights_v.allocation]

    if (target_sharpe_v <= vt_sharpe):
        target_returns_v, target_std_v = vt_return, vt_volatility
        target_sharpe_v = vt_sharpe
        targetPortfolio_v['x'] = [0, 1]

    # Print the weights of the Portfolio Matching 100% Volatility
    print("Weights for Portfolio Matching 100% VT Volatility):")
    for stock, weight in zip(meanReturns.index, targetPortfolio_v['x']):
        print(f"{stock}: {weight:.4f}")

    # Print the annualized returns, annualized volatility, and Sharpe Ratio as percentages
    print(f"\nAnnualized Return of the Portfolio Matching 100% Volatility: {target_returns_v * 100:.2f}%")
    print(f"Annualized Volatility of the Portfolio Matching 100% Volatility: {target_std_v * 100:.2f}%")
    print(f"Sharpe Ratio of the Portfolio Matching 100% Volatility {target_sharpe_v:.4f}\n")

    targetPortfolio_r = calculateTargetPortfolio_r(meanReturns, covMatrix, vt_return, cml_volatility, constraintSet)
    target_returns_r, target_std_r = portfolioPerformance(targetPortfolio_r['x'], meanReturns, covMatrix, riskFreeRate, leverageCost)
    target_sharpe_r = (target_returns_r - riskFreeRate) / target_std_r
    target_weights_r = pd.DataFrame(targetPortfolio_r['x'], index=meanReturns.index, columns=['allocation'])
    target_weights_r.allocation = [round(i * 100, 2) for i in target_weights_r.allocation]

    if (target_sharpe_r <= vt_sharpe):
        target_returns_r, target_std_r = vt_return, vt_volatility
        target_sharpe_r = vt_sharpe
        targetPortfolio_r['x'] = [0, 1]

    # Print the weights of the Portfolio Matching 100% Volatility
    print("Weights for Portfolio Matching 100% VT Returns):")
    for stock, weight in zip(meanReturns.index, targetPortfolio_r['x']):
        print(f"{stock}: {weight:.4f}")

    # Print the annualized returns, annualized volatility, and Sharpe Ratio as percentages
    print(f"\nAnnualized Return of the Portfolio Matching 100% Returns: {target_returns_r * 100:.2f}%")
    print(f"Annualized Volatility of the Portfolio Matching 100% Returns: {target_std_r * 100:.2f}%")
    print(f"Sharpe Ratio of the Portfolio Matching 100% Returns {target_sharpe_r:.4f}\n")

    maxSR_returns, maxSR_std = round(maxSR_returns * 100, 2), round(maxSR_std * 100, 2)
    minVol_returns, minVol_std = round(minVol_returns * 100, 2), round(minVol_std * 100, 2)

    vt_return, vt_volatility = round(vt_return * 100, 2), round(vt_volatility * 100, 2)
    bnd_return, bnd_volatility = round(bnd_return * 100, 2), round(bnd_volatility * 100, 2)

    target_returns_v, target_std_v= round(target_returns_v * 100, 2), round(target_std_v * 100, 2)
    target_returns_r, target_std_r= round(target_returns_r * 100, 2), round(target_std_r * 100, 2)

    return maxSR_returns, maxSR_std, maxSR_allocation, minVol_returns, minVol_std, minVol_allocation, vt_return, vt_volatility, bnd_return, bnd_volatility, target_returns_r, target_std_r, target_returns_v, target_std_v, efficientList, targetReturns

def EF_graph(meanReturns, covMatrix, riskFreeRate=0.0241, leverageCost=0.04, constraintSet=(0, 1)):
    """Return a graph plotting the min vol, max sr, efficient frontier, and tangency line"""
    maxSR_returns, maxSR_std, maxSR_allocation, minVol_returns, minVol_std, minVol_allocation, vt_return, vt_volatility, bnd_return, bnd_volatility, target_returns_r, target_std_r, target_returns_v, target_std_v, efficientList, targetReturns = calculatedResults(meanReturns, covMatrix, riskFreeRate, leverageCost, constraintSet)

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

    # 100% VT
    Vt = go.Scatter(
        name='100% VT Portfolio',
        mode='markers',
        x=[vt_volatility],
        y=[vt_return],
        marker=dict(color='orange', size=14, line=dict(width=3, color='black'))
    )

    # 100% BND
    Bnd = go.Scatter(
        name='100% BND Portfolio',
        mode='markers',
        x=[bnd_volatility],
        y=[bnd_return],
        marker=dict(color='blue', size=14, line=dict(width=3, color='black'))
    )

    # Portfolio Matching 100% VT Volatility
    Cml_Vt_Vol = go.Scatter(
        name='Portfolio Matching 100% VT Volatility',
        mode='markers',
        x=[target_std_v],
        y=[target_returns_v],
        marker=dict(color='purple', size=14, line=dict(width=3, color='black'))
    )

    # Portfolio Matching 100% VT Return
    Cml_Vt_Ret = go.Scatter(
        name='Portfolio Matching 100% VT Return',
        mode='markers',
        x=[target_std_r],
        y=[target_returns_r],
        marker=dict(color='pink', size=14, line=dict(width=3, color='black'))
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

    x_max = vt_volatility * 1.25
    y_max = vt_return * 1.25

    data = [TangencyPortfolio, MinVol, EF_curve, CML, Vt, Bnd, Cml_Vt_Vol, Cml_Vt_Ret]

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

EF_graph(meanReturns, covMatrix)

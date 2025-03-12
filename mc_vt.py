import yfinance as yf
import datetime as dt
import numpy as np
import matplotlib.pyplot as plt
import pandas as pd

# Download the stock data
stock_data = yf.download('VT', '2007-04-03', dt.datetime.now())
dividends = yf.Ticker('VT').dividends
price_data = yf.Ticker('VT').history(period="max")

yields = {}
annual_dividends = dividends.groupby(dividends.index.year).sum()

# Calculate the average annual closing price
annual_prices = price_data['Close'].resample('YE').mean()

# Ensure the years match between dividends and prices
annual_dividends = annual_dividends[annual_dividends.index.isin(annual_prices.index.year)]
annual_prices = annual_prices[annual_prices.index.year.isin(annual_dividends.index)]

# Calculate the annual dividend yield
annual_yields = (annual_dividends / annual_prices.values)

# Calculate the average annual dividend yield
average_quarterly_yield = annual_yields.mean() / 4

# Calculate daily returns
returns = stock_data['Close'].pct_change()

meanReturns = returns.mean()

# Assume 10.5 trading days per biweek
trading_days = 10.5

# Calculate bi-weekly return and volatility
biweekly_return = meanReturns * trading_days  # Use the return directly
biweekly_volatility = returns.std() * np.sqrt(trading_days)  # Use the volatility directly

# Monte Carlo Simulation Parameters
initial_investment = 54493.92  # Set initial investment amount
initial_contribution = 349.21  # Set the initial bi-weekly contribution
periods = 24 * 8  # Number of bi-weekly periods
simulations = 10000  # Number of simulations

# Simulate the growth of investment over 240 bi-weekly periods
final_values = []

for _ in range(simulations):
    print(f"Trial {_}")
    portfolio_value = initial_investment
    contribution = initial_contribution
    portfolio_values = [portfolio_value]  # Initialize with the starting value

    # Simulate the growth of investment and contributions over time
    for i in range(periods):
        # Simulate random returns using a log-normal distribution
        # The log-normal distribution requires the mean and volatility of the log returns
        random_return = np.random.lognormal(mean=biweekly_return, sigma=biweekly_volatility)
        # Update the portfolio value
        portfolio_value *= random_return
        portfolio_value += contribution  # Add the bi-weekly contribution
        if (i + 1) % 6 == 0:
            portfolio_value += average_quarterly_yield * portfolio_value

        # Every 24 periods (every year), increase the contribution by 3%
        if (i + 1) % 24 == 0:
            contribution *= 1.03  # Increase contribution by 3%

        portfolio_values.append(portfolio_value)

    final_values.append(portfolio_values[-1])  # Capture the final portfolio value after all periods

# Convert final values to a numpy array for easier statistics
final_values = np.array(final_values)

# Clip negative values to 0
final_values = np.clip(final_values, 0, None)

# Calculate percentiles
percentiles = np.percentile(final_values, [5, 10, 15, 20, 25, 30, 35, 40, 45, 50, 55, 60, 65, 70, 75, 80, 85, 90, 95])

# Calculate mean, median, and standard deviation
mean_value = final_values.mean()
median_value = np.median(final_values)
std_deviation = final_values.std()

# Print mean, median, and standard deviation
print(f"Mean Final Value: ${mean_value:,.2f}")
print(f"Median Final Value: ${median_value:,.2f}")
print(f"Standard Deviation of Final Value: ${std_deviation:,.2f}")

# Print percentiles
print("\nPercentiles (Dollar Amount):")
for percentile, value in zip(range(5, 100, 5), percentiles):
    print(f"{percentile}th Percentile: ${value:,.2f}")

# Plot the distribution of final portfolio values
plt.figure(figsize=(10, 6))
plt.hist(final_values, bins=50, color='blue', alpha=0.7, label='Final Portfolio Values')
plt.axvline(mean_value, color='r', linestyle='dashed', linewidth=2, label=f'Mean: ${mean_value:,.2f}')
plt.axvline(median_value, color='g', linestyle='dashed', linewidth=2, label=f'Median: ${median_value:,.2f}')
plt.title("Distribution of Final Portfolio Values from Monte Carlo Simulations (With Contributions and Log-Normal Returns)")
plt.xlabel("Portfolio Value ($)")
plt.ylabel("Frequency")
plt.legend()

# Mark percentiles on the plot
for percentile, value in zip(range(5, 100, 5), percentiles):
    plt.axvline(value, color='black', linestyle='dotted', linewidth=1)
    plt.text(value + 100, plt.gca().get_ylim()[1] * 0.02, f"{percentile}th", color='black', ha='center')

plt.tight_layout()
plt.show()

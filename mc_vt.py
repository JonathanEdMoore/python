import yfinance as yf
import datetime as dt
import numpy as np
import matplotlib.pyplot as plt
import pandas as pd

# Download the stock data
stock_data = yf.download('VT', '2007-04-03', dt.datetime.now())
dividends = yf.Ticker('VT').dividends
price_data = yf.Ticker('VT').history(period="max")

# Process dividend yield
annual_dividends = dividends.groupby(dividends.index.year).sum()
annual_prices = price_data['Close'].resample('YE').mean()

# Ensure years match
annual_dividends = annual_dividends[annual_dividends.index.isin(annual_prices.index.year)]
annual_prices = annual_prices[annual_prices.index.year.isin(annual_dividends.index)]

# Calculate average annual dividend yield
annual_yields = (annual_dividends / annual_prices.values)
average_quarterly_yield = annual_yields.mean() / 4

# Calculate daily returns
returns = stock_data['Close'].pct_change()
meanReturns = returns.mean()

# Assume 10.5 trading days per biweek
trading_days = 10.5

# Calculate bi-weekly return and volatility
biweekly_return = meanReturns * trading_days
biweekly_volatility = returns.std() * np.sqrt(trading_days)

# Monte Carlo Simulation Parameters
initial_investment = 65213.30
initial_contribution = 979.17  # Initial bi-weekly contribution
contribution_increase = 20.83  # Annual increase
initial_salary = 92_760  # Example starting salary
salary_growth = 1.03  # 3% salary growth per year
match_percentage = 0.04  # 4% employer match
periods = 24 * 28  # 8 years of bi-weekly periods
simulations = 1_000_000

# Simulate the growth of investment over 8 years
final_values = []

for _ in range(simulations):
    print(f"Trial {_}")
    portfolio_value = initial_investment
    contribution = initial_contribution
    salary = initial_salary
    portfolio_values = [portfolio_value]

    for i in range(periods):
        # Simulate returns using a log-normal distribution
        random_return = np.random.lognormal(mean=biweekly_return, sigma=biweekly_volatility)
        portfolio_value *= random_return

        # Employer match calculation
        employer_match = (salary * match_percentage) / 24
        total_contribution = contribution + employer_match

        portfolio_value += total_contribution

        # Apply quarterly dividends
        if (i + 1) % 6 == 0:
            portfolio_value += average_quarterly_yield * portfolio_value

        # Every 24 periods (1 year), increase contribution and salary
        if (i + 1) % 24 == 0:
            contribution += contribution_increase
            salary *= salary_growth  # Increase salary by 3%

        portfolio_values.append(portfolio_value)

    final_values.append(portfolio_values[-1])

# Convert final values to a numpy array
final_values = np.array(final_values)
final_values = np.clip(final_values, 0, None)  # Ensure no negative values

# Calculate statistics
percentiles = np.percentile(final_values, [5, 10, 15, 20, 25, 30, 35, 40, 45, 50, 55, 60, 65, 70, 75, 80, 85, 90, 95])
mean_value = final_values.mean()
median_value = np.median(final_values)
std_deviation = final_values.std()

# Print statistics
print(f"Mean Final Value: ${mean_value:,.2f}")
print(f"Median Final Value: ${median_value:,.2f}")
print(f"Standard Deviation of Final Value: ${std_deviation:,.2f}")

print("\nPercentiles (Dollar Amount):")
for percentile, value in zip(range(5, 100, 5), percentiles):
    print(f"{percentile}th Percentile: ${value:,.2f}")

# Plot results
plt.figure(figsize=(12, 6))
plt.hist(final_values, bins=50, color='blue', alpha=0.7, label='Final Portfolio Values')
plt.axvline(mean_value, color='r', linestyle='dashed', linewidth=2, label=f'Mean: ${mean_value:,.2f}')
plt.axvline(median_value, color='g', linestyle='dashed', linewidth=2, label=f'Median: ${median_value:,.2f}')

plt.title("Monte Carlo Simulation: Final Portfolio Value (With Contributions & Employer Match)")
plt.xlabel("Portfolio Value ($)")
plt.ylabel("Frequency")
plt.legend()

# Set x-axis limits to ensure proper spacing
x_min, x_max = np.percentile(final_values, [1, 99])  # Focus on the central 98% range
plt.xlim(x_min * 0.9, x_max * 1.1)  # Add padding to the limits

# Set evenly spaced x-ticks
num_ticks = 10  # Adjust based on spread
tick_spacing = (x_max - x_min) / num_ticks
plt.xticks(np.arange(x_min, x_max, tick_spacing), rotation=45)

# Format x-axis labels
plt.ticklabel_format(style='plain', axis='x')  # Prevent scientific notation

for percentile, value in zip(range(5, 100, 5), percentiles):
    plt.axvline(value, color='black', linestyle='dotted', linewidth=1)
    plt.text(value, plt.gca().get_ylim()[1] * 0.02, f"{percentile}th", color='black', ha='center', rotation=45)

plt.tight_layout()
plt.show()


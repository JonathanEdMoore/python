import numpy as np
import matplotlib.pyplot as plt

# Simulation parameters
np.random.seed(42)  # For reproducibility
years = 28
initial_value = 54493.92
num_simulations = 1000000
contributions_per_year = 24  # Twice a month

# Contribution parameters
annual_contribution = float(input("Enter the annual contribution: "))  
inflation_rate = float(input("Enter the expected inflation rate (%): ")) / 100  

# Convert annual contribution to twice-monthly
twice_monthly_contribution = annual_contribution / contributions_per_year

# Portfolio A (Lower Volatility)
cagr_A = float(input("Enter the CAGR of Portfolio A: ")) / 100
volatility_A = float(input("Enter the volatility of Portfolio A: ")) / 100

# Portfolio B (Higher Volatility)
cagr_B = float(input("Enter the CAGR of Portfolio B: ")) / 100
volatility_B = float(input("Enter the volatility of Portfolio B: ")) / 100

# Convert annual return and volatility to half-monthly (1/24 of a year)
half_monthly_return_A = (1 + cagr_A) ** (1/contributions_per_year) - 1
half_monthly_volatility_A = volatility_A / np.sqrt(contributions_per_year)

half_monthly_return_B = (1 + cagr_B) ** (1/contributions_per_year) - 1
half_monthly_volatility_B = volatility_B / np.sqrt(contributions_per_year)

# Number of time periods
total_periods = years * contributions_per_year

# Generate random returns for all simulations at once (vectorized)
returns_A = np.random.normal(half_monthly_return_A, half_monthly_volatility_A, (num_simulations, total_periods))
returns_B = np.random.normal(half_monthly_return_B, half_monthly_volatility_B, (num_simulations, total_periods))

# Initialize portfolio values
portfolio_A = np.full((num_simulations,), initial_value)
portfolio_B = np.full((num_simulations,), initial_value)

# Generate contribution schedule with annual increases
contributions = np.full((total_periods,), twice_monthly_contribution)
for year in range(1, years):
    start_index = year * contributions_per_year
    contributions[start_index:] *= (1 + inflation_rate)  # Apply inflation annually

# Expand contributions to match number of simulations (vectorized)
contributions = np.tile(contributions, (num_simulations, 1))

# Compute portfolio growth (vectorized)
portfolio_A = (portfolio_A[:, None] + contributions) * (1 + returns_A)
portfolio_B = (portfolio_B[:, None] + contributions) * (1 + returns_B)

# Compute cumulative product to apply returns iteratively
portfolio_A = np.cumprod(portfolio_A, axis=1)[:, -1]  # Get final values
portfolio_B = np.cumprod(portfolio_B, axis=1)[:, -1]

# Ensure no negative values
portfolio_A = np.maximum(0, portfolio_A)
portfolio_B = np.maximum(0, portfolio_B)

# Compute probability that Portfolio A ends higher than Portfolio B
prob_A_higher = np.mean(portfolio_A > portfolio_B)
prob_B_higher = 1 - prob_A_higher

# Compute percentiles
percentiles_A = np.percentile(portfolio_A, np.arange(0, 101, 5))  # Every 5%
percentiles_B = np.percentile(portfolio_B, np.arange(0, 101, 5))  # Every 5%

# Plot histogram
plt.figure(figsize=(10, 6))
plt.hist(portfolio_A, bins=50, alpha=0.6, label="Portfolio A (Lower Volatility)")
plt.hist(portfolio_B, bins=50, alpha=0.6, label="Portfolio B (Higher Volatility)")
plt.axvline(np.median(portfolio_A), color='blue', linestyle='dashed', linewidth=2, label="Median A")
plt.axvline(np.median(portfolio_B), color='orange', linestyle='dashed', linewidth=2, label="Median B")

# Format x-axis with logarithmic scale for better readability
plt.xlabel("Final Portfolio Value (Millions)")
plt.ylabel("Frequency")
plt.legend()

# Ensure we don't attempt log10 of zero
min_value = min(np.min(portfolio_A), np.min(portfolio_B))
min_value = min_value if min_value > 0 else initial_value * 1e-6  # Set a small threshold

# Set the x-axis to a log scale
plt.xscale('log')

# Adjust the tick labels on the x-axis to show readable values in millions
plt.xticks([10**i for i in range(int(np.log10(min_value)), 
                                int(np.log10(max(portfolio_A.max(), portfolio_B.max()))) + 1)],
           labels=[f"${10**i / 1e6:.1f}M" for i in range(int(np.log10(min_value)), 
                                                       int(np.log10(max(portfolio_A.max(), portfolio_B.max()))) + 1)])

plt.title(f"Monte Carlo Simulation of Portfolio Growth\nPortfolio A ends higher {prob_A_higher:.1%} of the time")
plt.show()

# Print key results
print(f"\nProbability that Portfolio A (lower volatility) ends higher than Portfolio B: {prob_A_higher:.1%}")
print(f"Probability that Portfolio B (higher volatility) ends higher than Portfolio A: {prob_B_higher:.1%}\n")
print(f"Mean final value of Portfolio A: ${np.mean(portfolio_A):,.2f}")
print(f"Mean final value of Portfolio B: ${np.mean(portfolio_B):,.2f}\n")

print("\nPortfolio A (Lower Volatility) Percentiles:")
for i, p in enumerate(np.arange(0, 101, 5)):
    print(f"{p}th Percentile: ${percentiles_A[i]:,.2f}")

print("\nPortfolio B (Higher Volatility) Percentiles:")
for i, p in enumerate(np.arange(0, 101, 5)):
    print(f"{p}th Percentile: ${percentiles_B[i]:,.2f}")

import numpy as np
import matplotlib.pyplot as plt

# Simulation parameters
np.random.seed(42)  # For reproducibility
years = 28
initial_value = 54493.92
num_simulations = 1000000

# Portfolio A (Lower Volatility)
cagr_A = float(input("Enter the CAGR of Portfolio A: ")) / 100
volatility_A = float(input("Enter the volatility of Portfolio A: ")) / 100

# Portfolio B (Higher Volatility)
cagr_B = float(input("Enter the CAGR of Portfolio B: ")) / 100
volatility_B = float(input("Enter the volatility of Portfolio B: ")) / 100

# Monte Carlo simulations
final_values_A = []
final_values_B = []

for _ in range(num_simulations):
    # Generate annual returns using a normal distribution
    returns_A = np.random.normal(cagr_A, volatility_A, years)
    returns_B = np.random.normal(cagr_B, volatility_B, years)
    
    # Compute final portfolio values, ensuring lower bound at 0
    value_A = max(0, initial_value * np.prod(1 + returns_A))
    value_B = max(0, initial_value * np.prod(1 + returns_B))
    
    final_values_A.append(value_A)
    final_values_B.append(value_B)

# Convert lists to NumPy arrays for faster calculations
final_values_A = np.array(final_values_A)
final_values_B = np.array(final_values_B)

# Calculate probability that Portfolio A ends with a higher value than Portfolio B
prob_A_higher = np.mean(final_values_A > final_values_B)
prob_B_higher = 1 - prob_A_higher

# Compute percentiles
percentiles_A = np.percentile(final_values_A, np.arange(0, 101, 5))  # Every 5%
percentiles_B = np.percentile(final_values_B, np.arange(0, 101, 5))  # Every 5%

# Plot histogram
plt.figure(figsize=(10, 6))
plt.hist(final_values_A, bins=50, alpha=0.6, label="Portfolio A (Lower Volatility)")
plt.hist(final_values_B, bins=50, alpha=0.6, label="Portfolio B (Higher Volatility)")
plt.axvline(np.median(final_values_A), color='blue', linestyle='dashed', linewidth=2, label="Median A")
plt.axvline(np.median(final_values_B), color='orange', linestyle='dashed', linewidth=2, label="Median B")

# Format x-axis with logarithmic scale for better readability
plt.xlabel("Final Portfolio Value (Millions)")
plt.ylabel("Frequency")
plt.legend()

# Ensure we don't attempt log10 of zero
min_value = min(np.min(final_values_A), np.min(final_values_B))
min_value = min_value if min_value > 0 else initial_value * 1e-6  # Set a small threshold

# Set the x-axis to a log scale
plt.xscale('log')

# Adjust the tick labels on the x-axis to show readable values in millions
plt.xticks([10**i for i in range(int(np.log10(min_value)), 
                                int(np.log10(max(final_values_A.max(), final_values_B.max()))) + 1)],
           labels=[f"${10**i / 1e6:.1f}M" for i in range(int(np.log10(min_value)), 
                                                       int(np.log10(max(final_values_A.max(), final_values_B.max()))) + 1)])

plt.title(f"Monte Carlo Simulation of Portfolio Growth\nPortfolio A ends higher {prob_A_higher:.1%} of the time")
plt.show()

# Print key results
print(f"\nProbability that Portfolio A (lower volatility) ends higher than Portfolio B: {prob_A_higher:.1%}")
print(f"Probability that Portfolio B (higher volatility) ends higher than Portfolio A: {prob_B_higher:.1%}\n")
print(f"Mean final value of Portfolio A: ${np.mean(final_values_A):,.2f}")
print(f"Mean final value of Portfolio B: ${np.mean(final_values_B):,.2f}\n")

print("\nPortfolio A (Lower Volatility) Percentiles:")
for i, p in enumerate(np.arange(0, 101, 5)):
    print(f"{p}th Percentile: ${percentiles_A[i]:,.2f}")

print("\nPortfolio B (Higher Volatility) Percentiles:")
for i, p in enumerate(np.arange(0, 101, 5)):
    print(f"{p}th Percentile: ${percentiles_B[i]:,.2f}")
import numpy as np
import matplotlib.pyplot as plt

# Simulation parameters
np.random.seed(42)  # For reproducibility
years = 30
initial_value = 100000
num_simulations = 1000

# Portfolio A (Lower Volatility)
cagr_A = float(input("Enter the CAGR of Portfolio A): "))
volatility_A = float(input("Enter the volatility of Portfolio A): "))

# Portfolio B (Higher Volatility)
cagr_B = float(input("Enter the CAGR of Portfolio B): "))
volatility_B = float(input("Enter the volatility of Portfolio B): "))

# Monte Carlo simulations
final_values_A = []
final_values_B = []

for _ in range(num_simulations):
    # Generate annual returns using a normal distribution
    returns_A = np.random.normal(cagr_A, volatility_A, years)
    returns_B = np.random.normal(cagr_B, volatility_B, years)
    
    # Compute final portfolio values
    value_A = initial_value * np.prod(1 + returns_A)
    value_B = initial_value * np.prod(1 + returns_B)
    
    final_values_A.append(value_A)
    final_values_B.append(value_B)

# Calculate probability that Portfolio A ends with a higher value than Portfolio B
prob_A_higher = np.mean(np.array(final_values_A) > np.array(final_values_B))
prob_B_higher = 1 - prob_A_higher

# Plot histogram
plt.figure(figsize=(10, 6))
plt.hist(final_values_A, bins=50, alpha=0.6, label="Portfolio A (Lower Volatility)")
plt.hist(final_values_B, bins=50, alpha=0.6, label="Portfolio B (Higher Volatility)")
plt.axvline(np.median(final_values_A), color='blue', linestyle='dashed', linewidth=2, label="Median A")
plt.axvline(np.median(final_values_B), color='orange', linestyle='dashed', linewidth=2, label="Median B")
plt.xlabel("Final Portfolio Value ($)")
plt.ylabel("Frequency")
plt.legend()
plt.title(f"Monte Carlo Simulation of Portfolio Growth\nPortfolio A ends higher {prob_A_higher:.1%} of the time")
plt.show()

# Print key results
print(f"Probability that Portfolio A (lower volatility) ends higher than Portfolio B: {prob_A_higher:.1%}")
print(f"Probability that Portfolio B (higher volatility) ends higher than Portfolio A: {prob_B_higher:.1%}")
print(f"Median final value of Portfolio A: ${np.median(final_values_A):,.2f}")
print(f"Median final value of Portfolio B: ${np.median(final_values_B):,.2f}")

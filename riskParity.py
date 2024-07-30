import numpy as np
from scipy.optimize import minimize

# Asset volatilities
volatilities = np.array([0.20, 0.05, 0.15])

# Covariance matrix
cov_matrix = np.array([
    [0.04, 0.01, 0.02],
    [0.01, 0.0025, 0.005],
    [0.02, 0.005, 0.0225]
])

# Number of assets
num_assets = len(volatilities)

# Objective function: sum of squared differences of risk contributions
def risk_parity_objective(weights):
    portfolio_variance = np.dot(weights.T, np.dot(cov_matrix, weights))
    marginal_risk_contributions = np.dot(cov_matrix, weights)
    risk_contributions = weights * marginal_risk_contributions
    risk_contributions = risk_contributions / portfolio_variance
    return np.sum((risk_contributions - 1/num_assets)**2)

# Constraints: weights sum to 1
constraints = ({'type': 'ineq', 'fun': lambda weights: np.sum(weights) - 1})

# Bounds: weights between 0 and 1
bounds = tuple((0, 1) for _ in range(num_assets))

# Initial guess: equally weighted portfolio
initial_weights = np.ones(num_assets) / num_assets

# Optimize weights
result = minimize(risk_parity_objective, initial_weights, method='SLSQP', bounds=bounds, constraints=constraints)

# Optimal weights
optimal_weights = result.x
print(optimal_weights)

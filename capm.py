risk_free_rate = float(input("Please enter the Risk Free Rate: ")) / 100
beta = float(input("Please enter the Beta of the asset or portfolio: "))
market_return = float(input("Please enter the Market Return: ")) / 100
actual_return = float(input("Please enter the Actual Return of the asset or portfolio: ")) / 100

expected_return = risk_free_rate + beta * (market_return - risk_free_rate)

alpha = actual_return - expected_return

print(f"Expected Return: {expected_return * 100:.2f}%")
print(f"Alpha: {alpha * 100:.2f}%")
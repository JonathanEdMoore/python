def pension_value(C0, i, r, n):
    total_value = 0
    for t in range(1, n+1):
        Ct = C0 * (1 + i)**(t-1)
        PVt = Ct / (1 + r)**t
        total_value += PVt
    return total_value

# Example Parameters
C0 = 400000  # Initial payment
i = 0.02     # Inflation rate (2%)
r = 0.05     # Discount rate (5%)
n = 30       # Number of years

value = pension_value(C0, i, r, n)
print(f"The estimated value of the pension is ${value:,.2f}")


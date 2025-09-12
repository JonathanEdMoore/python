import numpy as np

def dcf_monthly(initial_monthly_cash_flow, annual_growth_rate, annual_discount_rate, years, terminal_value_multiple):
    # Convert to monthly rates
    monthly_growth_rate = (1 + annual_growth_rate) ** (1/12) - 1
    monthly_discount_rate = (1 + annual_discount_rate) ** (1/12) - 1
    months = years * 12

    cash_flows = []
    discounted_cash_flows = []

    # Calculate net cash flows and present values month by month
    for month in range(1, months + 1):
        cash_flow = initial_monthly_cash_flow * (1 + monthly_growth_rate) ** (month - 1)
        discounted_cash_flow = cash_flow / (1 + monthly_discount_rate) ** month
        cash_flows.append(cash_flow)
        discounted_cash_flows.append(discounted_cash_flow)

    # Terminal value (multiple of last month’s cash flow)
    terminal_value = cash_flows[-1] * terminal_value_multiple
    discounted_terminal_value = terminal_value / (1 + monthly_discount_rate) ** months

    intrinsic_value = np.sum(discounted_cash_flows) + discounted_terminal_value
    return intrinsic_value


# Example: $500 monthly UBI for 70 years
monthly_ubi = 500
growth_rate = 0.025   # annual growth (2%)
discount_rate = 0.045  # annual discount rate (4.5%)
years = 75
terminal_value_multiple = 0  # UBI has no resale value

print(f"\nUBI Intrinsic value: ${dcf_monthly(monthly_ubi, growth_rate, discount_rate, years, terminal_value_multiple):,.2f}")

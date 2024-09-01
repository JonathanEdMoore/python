import numpy as np

def dcf(initial_cash_flow, growth_rate, discount_rate, years, terminal_value_multiple):
  # Initialize variables
  cash_flows = []
  discounted_cash_flows = []

  # Calculate net cash flows and their present value for each year
  for year in range(1, years + 1):
    cash_flow = initial_cash_flow * (1 + growth_rate) ** (year - 1)
    discounted_cash_flow = cash_flow / (1 + discount_rate) ** year
    cash_flows.append(cash_flow)
    discounted_cash_flows.append(discounted_cash_flow)

  # Calculate terminal value (15x the final year's cash flow)
  terminal_value = cash_flows[-1] * terminal_value_multiple
  discounted_terminal_value = terminal_value / (1 + discount_rate) ** years

  # Sum the discounted cash flows and the discounted terminal value
  intrinsic_value = np.sum(discounted_cash_flows) + discounted_terminal_value

  return intrinsic_value

# Assumptions
initial_cash_flow = 19000  # Year 1 net cash flow
growth_rate = 0.02  # 2% growth rate of cash flow
discount_rate = 0.07  # 7% discount rate
years = 30  # Projection period
terminal_value_multiple = 15  # Multiple of the final year's cash flow

# print(dcf(initial_cash_flow, growth_rate, discount_rate, years, terminal_value_multiple))

annual_ubi = 12000
years = 60
terminal_value_multiple = 0 # Can't sell the UBI as an asset

print(f"\nUBI Intrinsic value: ${dcf(annual_ubi, growth_rate, discount_rate, years, terminal_value_multiple):,.2f}")

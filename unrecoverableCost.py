def wacc_with_pmi(price_of_home, down_payment_percent, cost_of_equity, cost_of_debt, mortgage_term_years, closing_cost_percent=0, pmi_rate=0):
    # Initial values
    down_payment = price_of_home * down_payment_percent
    closing_costs = price_of_home * closing_cost_percent
    mortgage = price_of_home - down_payment
    monthly_rate = cost_of_debt / 12
    num_payments = mortgage_term_years * 12

    # Monthly mortgage payment
    monthly_payment = (mortgage * monthly_rate * (1 + monthly_rate)**num_payments) / ((1 + monthly_rate)**num_payments - 1)
    print(f"\nMonthly Payment: ${monthly_payment:,.2f}\n")

    total_wacc = 0
    pmi_total = 0
    remaining_principal = mortgage

    for year in range(mortgage_term_years):
        for month in range(12):
            interest_payment = remaining_principal * monthly_rate
            principal_payment = monthly_payment - interest_payment
            remaining_principal -= principal_payment

        equity = price_of_home - remaining_principal
        total_value = price_of_home
        ltv = remaining_principal / price_of_home

        if ltv > 0.80:
            effective_cost_of_debt = cost_of_debt + pmi_rate
            pmi_annual = mortgage * pmi_rate
            pmi_total += pmi_annual
        else:
            effective_cost_of_debt = cost_of_debt

        wacc_t = (remaining_principal / total_value) * effective_cost_of_debt + (equity / total_value) * cost_of_equity
        total_wacc += wacc_t

    average_wacc = total_wacc / mortgage_term_years
    return average_wacc, pmi_total, closing_costs


# Inputs
price_of_home = float(input("Enter the price of the home: "))
down_payment_percent = float(input("Enter the down payment percentage: "))
mortgage_term_years = int(input("Enter the mortgage term years: "))
property_tax = float(input("Enter the property tax: "))
hoa = float(input("Enter the HOA/Maintenance rate: "))
insurance = float(input("Enter the insurance rate: "))
cost_of_debt = float(input("Enter the mortgage interest rate: "))
pe = float(input("Enter the CAPE ratio: "))
target_pe = float(input("Enter the Target CAPE ratio: "))
valuation_change = (target_pe / pe) ** (1 / 10) - 1
earnings_growth = float(input("Enter the expected earnings growth: "))
expected_return_real_estate = float(input("Enter the expected return of real estate: "))
expected_return_stocks = (1 / pe) + earnings_growth + valuation_change
cost_of_equity = expected_return_stocks - expected_return_real_estate
pmi_rate = float(input("Enter the private mortgage insurance rate: "))
closing_cost_percent = float(input("Enter the closing cost percentage: ")) # 3% closing costs

# Run WACC calculation
average_cost_of_capital, pmi_total, closing_costs = wacc_with_pmi(
    price_of_home,
    down_payment_percent,
    cost_of_equity,
    cost_of_debt,
    mortgage_term_years,
    closing_cost_percent,
    pmi_rate
)

down_payment = price_of_home * down_payment_percent
capital_invested = down_payment + closing_costs
unrecoverable_cost = (average_cost_of_capital + property_tax + hoa + insurance) * price_of_home + (closing_costs / mortgage_term_years)
rent = unrecoverable_cost

# Outputs
print(f"Down Payment: ${down_payment:,.2f}")
print(f"Closing Costs: ${closing_costs:,.2f}")
print(f"Capital Invested: ${capital_invested:,.2f}")
print(f"Cost of Debt: {cost_of_debt * 100:.2f}%")
print(f"Cost of Equity: {cost_of_equity * 100:.2f}%")
print(f"Total PMI Paid: ${pmi_total:,.2f}")
print(f"Annual Required Home Savings: ${(property_tax + hoa + insurance) * price_of_home:,.2f}")
print(f"Annual Unrecoverable Costs: ${unrecoverable_cost:,.2f}")
print(f"Monthly Required Home Savings: ${((property_tax + hoa + insurance) * price_of_home) / 12:,.2f}")
print(f"Monthly Unrecoverable Costs: ${unrecoverable_cost / 12:,.2f}")
print(f"Annual Income Needed: ${unrecoverable_cost / 0.3:,.2f}")

# Recalculate home price based on rent
price_of_home_estimate = (rent - (closing_costs / mortgage_term_years)) / (average_cost_of_capital + property_tax + hoa + insurance)
print(f"\nAnnual Rent: ${rent:,.2f}")
print(f"Monthly Rent: ${rent / 12:,.2f}")
print(f"Estimated Value of Home: ${price_of_home_estimate:,.2f}")

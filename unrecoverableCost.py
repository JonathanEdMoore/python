from scipy.optimize import minimize_scalar

def wacc_with_pmi(price_of_home, down_payment_percent, cost_of_equity, cost_of_debt, mortgage_term_years, closing_cost_percent=0, pmi_rate=0):
    down_payment = price_of_home * down_payment_percent
    closing_costs = price_of_home * closing_cost_percent
    mortgage = price_of_home - down_payment
    monthly_rate = cost_of_debt / 12
    num_payments = mortgage_term_years * 12

    # Monthly mortgage payment (excluding PMI)
    monthly_payment = (mortgage * monthly_rate * (1 + monthly_rate)**num_payments) / ((1 + monthly_rate)**num_payments - 1)

    total_wacc = 0
    pmi_total = 0
    remaining_principal = mortgage

    for year in range(mortgage_term_years):
        for month in range(12):
            # Step 1: Calculate LTV before payment
            ltv = remaining_principal / price_of_home
            equity = price_of_home - remaining_principal

            # Step 2: Check if PMI applies
            if ltv > 0.80:
                monthly_pmi = mortgage * pmi_rate / 12
                pmi_total += monthly_pmi
                effective_cost_of_debt = cost_of_debt + pmi_rate
            else:
                monthly_pmi = 0
                effective_cost_of_debt = cost_of_debt

            # Step 3: Compute monthly interest and principal
            interest_payment = remaining_principal * monthly_rate
            principal_payment = monthly_payment - interest_payment
            remaining_principal -= principal_payment

            # Step 4: Compute WACC for this month
            debt_weight = remaining_principal / price_of_home
            equity_weight = equity / price_of_home
            monthly_wacc = debt_weight * effective_cost_of_debt + equity_weight * cost_of_equity
            total_wacc += monthly_wacc

    average_wacc = total_wacc / (mortgage_term_years * 12)
    return average_wacc, pmi_total, closing_costs, monthly_payment



def unrecoverable_cost_given_down_payment(down_payment_percent, *args):
    price_of_home, cost_of_equity, cost_of_debt, mortgage_term_years, closing_cost_percent, pmi_rate, property_tax, hoa, insurance = args
    
    avg_wacc, _, closing_costs, _ = wacc_with_pmi(
        price_of_home,
        down_payment_percent,
        cost_of_equity,
        cost_of_debt,
        mortgage_term_years,
        closing_cost_percent,
        pmi_rate
    )
    
    unrecoverable_cost = (avg_wacc + property_tax + hoa + insurance) * price_of_home + (closing_costs / mortgage_term_years)
    return unrecoverable_cost

def find_optimal_down_payment_percent(price_of_home, cost_of_equity, cost_of_debt, mortgage_term_years, closing_cost_percent, pmi_rate, property_tax, hoa, insurance):
    result = minimize_scalar(
        unrecoverable_cost_given_down_payment,
        bounds=(0.0, 1.0),
        method='bounded',
        args=(price_of_home, cost_of_equity, cost_of_debt, mortgage_term_years, closing_cost_percent, pmi_rate, property_tax, hoa, insurance)
    )
    
    return result.x, result.fun  # optimal down payment %, minimum unrecoverable cost
# Inputs
price_of_home = float(input("Enter the price of the home: "))
down_payment_percent = float(input("Enter the down payment percentage: "))
mortgage_term_years = int(input("Enter the mortgage term years: "))
cost_of_debt = float(input("Enter the mortgage interest rate: "))
property_tax = float(input("Enter the property tax: "))
hoa = float(input("Enter the HOA/Maintenance rate: "))
insurance = float(input("Enter the insurance rate: "))
pmi_rate = float(input("Enter the private mortgage insurance rate: "))
pe = float(input("Enter the CAPE ratio: "))
target_pe = float(input("Enter the Target CAPE ratio: "))
valuation_change = (target_pe / pe) ** (1 / 10) - 1
earnings_growth = float(input("Enter the expected earnings growth: "))
expected_return_real_estate = float(input("Enter the expected return of real estate: "))
expected_return_stocks = (1 / pe) + earnings_growth + valuation_change
cost_of_equity = expected_return_stocks - expected_return_real_estate
closing_cost_percent = float(input("Enter the closing cost percentage: ")) # 3% closing costs

# Run WACC calculation
average_cost_of_capital, pmi_total, closing_costs, monthly_payment = wacc_with_pmi(
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

optimal_dp_percent, min_unrec_cost = find_optimal_down_payment_percent(
    price_of_home,
    cost_of_equity,
    cost_of_debt,
    mortgage_term_years,
    closing_cost_percent,
    pmi_rate,
    property_tax,
    hoa,
    insurance
)

# Outputs
print(f"\nMonthly Payment: ${monthly_payment:,.2f}")
print(f"\nDown Payment: ${down_payment:,.2f}")
print(f"Closing Costs: ${closing_costs:,.2f}")
print(f"Capital Invested: ${capital_invested:,.2f}")
print(f"Cost of Debt: {cost_of_debt * 100:.2f}%")
print(f"Cost of Equity: {cost_of_equity * 100:.2f}%")
print(f"Total PMI Paid: ${pmi_total:,.2f}")
print(f"Annual Required Home Savings: ${(property_tax + hoa + insurance) * price_of_home:,.2f}")
print(f"Monthly Required Home Savings: ${((property_tax + hoa + insurance) * price_of_home) / 12:,.2f}")
print(f"Annual Unrecoverable Costs: ${unrecoverable_cost:,.2f}")
print(f"Monthly Unrecoverable Costs: ${unrecoverable_cost / 12:,.2f}")
print(f"Annual Income Needed: ${unrecoverable_cost / 0.3:,.2f}")

# Recalculate home price based on rent
price_of_home_estimate = (rent - (closing_costs / mortgage_term_years)) / (average_cost_of_capital + property_tax + hoa + insurance)
print(f"\nAnnual Rent: ${rent:,.2f}")
print(f"Monthly Rent: ${rent / 12:,.2f}")
print(f"Estimated Value of Home: ${price_of_home_estimate:,.2f}")

print(f"\nOptimal Down Payment %: {optimal_dp_percent * 100}%")
print(f"Minimum Unrecoverable Cost: ${min_unrec_cost:,.2f}\n")

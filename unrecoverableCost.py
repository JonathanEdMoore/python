def wacc_with_pmi(price_of_home, down_payment_percent, cost_of_equity, cost_of_debt, mortgage_term_years, pmi_rate=0):
    # Initial values
    down_payment = price_of_home * down_payment_percent
    mortgage = price_of_home - down_payment  # Initial loan amount
    monthly_rate = cost_of_debt / 12  # Monthly interest rate
    num_payments = mortgage_term_years * 12  # Total number of payments

    # Monthly mortgage payment
    monthly_payment = (mortgage * monthly_rate * (1 + monthly_rate)**num_payments) / ((1 + monthly_rate)**num_payments - 1)
    print(f"\nMonthly Payment: ${monthly_payment:,.2f}\n")

    # Variables to store the sum of WACC over the years
    total_wacc = 0
    pmi_total = 0  # Track total PMI paid

    # Remaining principal starts as the full mortgage
    remaining_principal = mortgage

    # Loop through each year to calculate WACC for that year
    for year in range(mortgage_term_years):
        # Calculate remaining principal after 'year' years (after 12 * year payments)
        for month in range(12):  # Iterate through 12 months for each year
            interest_payment = remaining_principal * monthly_rate
            principal_payment = monthly_payment - interest_payment
            remaining_principal -= principal_payment

        # Equity increases as the remaining principal decreases
        equity = price_of_home - remaining_principal  # Home equity at year t
        total_value = price_of_home  # Total value (home price remains constant)

        # Calculate LTV ratio
        ltv = remaining_principal / price_of_home

        # Adjust the cost of debt to include PMI if LTV is above 80%
        if ltv > 0.80:
            effective_cost_of_debt = cost_of_debt + pmi_rate  # Adding PMI rate to the cost of debt
            pmi_annual = mortgage * pmi_rate  # PMI is a percentage of the original loan amount
            pmi_total += pmi_annual  # Accumulate PMI costs
        else:
            effective_cost_of_debt = cost_of_debt  # No PMI once LTV <= 80%

        # WACC at time t with adjusted cost of debt
        wacc_t = (remaining_principal / total_value) * effective_cost_of_debt + (equity / total_value) * cost_of_equity
        
        # Add WACC of year t to the total
        total_wacc += wacc_t

    # Calculate the average WACC over the full mortgage term
    average_wacc = total_wacc / (mortgage_term_years + 1)  # Including year 0
    return average_wacc, pmi_total  # Return both WACC and total PMI paid

# Inputs
price_of_home = 1291043.55
rent = 10000 * 12
down_payment_percent = 0.035
down_payment = price_of_home * down_payment_percent
mortgage_term_years = 15
property_tax = 0.0189
hoa = 0.01  # HOA fees
insurance = 0.005
cost_of_debt = 0.05468
expected_return_real_estate = 0.03
expected_return_stocks = 0.1
cost_of_equity = expected_return_stocks - expected_return_real_estate

# PMI rate (example: 0.5% annually)
pmi_rate = 0.005  # Adjust PMI percentage based on loan terms

# WACC with PMI calculation
average_cost_of_capital, pmi_total = wacc_with_pmi(price_of_home, down_payment_percent, cost_of_equity, cost_of_debt, mortgage_term_years, pmi_rate)

# Include PMI in the unrecoverable costs
unrecoverable_cost = (average_cost_of_capital + property_tax + hoa + insurance) * price_of_home

# Outputs
print(f"Down Payment: ${down_payment:,.2f}")
print(f"Total PMI Paid: ${pmi_total:,.2f}")
print(f"Annual Unrecoverable Costs: ${unrecoverable_cost:,.2f}")
print(f"Monthly Unrecoverable Costs: ${unrecoverable_cost / 12:,.2f}")
print(f"Annual Income Needed: ${unrecoverable_cost / 0.3:,.2f}\n")

# Recalculate home price based on rent and unrecoverable costs
price_of_home = rent / (average_cost_of_capital + property_tax + hoa + insurance)
print(f"Annual Rent: ${rent:,.2f}")
print(f"Monthly Rent: ${rent / 12:,.2f}")
print(f"Estimated Value of Home: ${price_of_home:,.2f}\n")

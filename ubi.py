import numpy as np
import pandas as pd
import json

def future_value_annuity(pmt, rate, periods):
    """Calculate the future value of an annuity."""
    r = rate / 12  # Monthly interest rate
    n = periods * 12  # Total number of monthly payments
    return pmt * ((1 + r)**n - 1) / r

def present_value_future_value(fv, rate, periods):
    """Calculate the present value needed to match a future value."""
    r = rate / 12  # Monthly interest rate
    n = periods * 12  # Total number of monthly payments
    return fv / ((1 + r)**n)

def calculate_fv_and_pv_for_ages(start_age, end_age, initial_monthly_payment, annual_rate, inflation_rate):
    """Calculate the future value and present value for each age, adjusting for inflation."""
    results = {}
    for age in range(start_age, end_age):
        years_invested = 80 - age
        
        # Adjust monthly payment for inflation
        inflated_monthly_payment = initial_monthly_payment * ((1 + inflation_rate) ** (years_invested))
        
        fv = future_value_annuity(inflated_monthly_payment, annual_rate, years_invested)
        pv = present_value_future_value(fv, annual_rate, years_invested)
        results[age] = {'Future Value': fv, 'Lump Sum Needed': pv}
    
    return results

def calculate_total_cost(age_distribution, lump_sums):
    """Calculate the total cost of providing lump sums to the population."""
    total_cost = sum(age_distribution[age] * lump_sums.get(age, 0) for age in age_distribution)
    return total_cost

# Parameters
start_age = 18
end_age = 19  # Updated to include all ages from 18 to 19
initial_monthly_payment = 1000
annual_rate = 0.03
inflation_rate = 0.02  # Example annual inflation rate

# Age distribution (number of U.S. citizens at each age)
age_distribution = {}

with open('demographic.json', 'r') as file:
    json_string = file.read()

demographics = json.loads(json_string)

# Function to process age groups
def process_age_groups(age_groups):
    for age in age_groups:
        ageKey = int(age['age'])
        if 18 <= ageKey <= 18:  # Filter ages within the range 18 to 19
            if ageKey not in age_distribution:
                age_distribution[ageKey] = 0
            age_distribution[ageKey] += age['actual_value']

# Process male demographics
process_age_groups(demographics['male']['values'][0]['age_groups'])

# Process female demographics
process_age_groups(demographics['female']['values'][0]['age_groups'])

# Calculate future values and lump sums
results = calculate_fv_and_pv_for_ages(start_age, end_age, initial_monthly_payment, annual_rate, inflation_rate)

# Extract lump sums from results
lump_sums = {age: results[age]['Lump Sum Needed'] for age in results}

# Calculate the total cost
total_cost = calculate_total_cost(age_distribution, lump_sums)

# Convert to dollars for readability
total_cost_formatted = '${:,.2f}'.format(total_cost)

print(f"Total Cost to Provide Age-Appropriate Lump Sums: {total_cost_formatted}")

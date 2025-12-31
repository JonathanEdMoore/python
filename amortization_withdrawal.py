def pmt(rate, nper, pv, fv=0, when=0):
    """
    Recreate Excel's PMT function.
    """
    if rate == 0:
        return -(pv + fv) / nper

    factor = (1 + rate)**nper
    return -(pv * factor + fv) / ((1 + rate * when) * (factor - 1) / rate)

# --- User Inputs ---
total_portfolio_start = float(input("Enter total portfolio at start of period: "))
liability_portion = float(input("Enter liability portion at start of period: "))
essential_withdrawal = float(input("Enter essential withdrawal for this period: "))
total_portfolio_after_market = float(input("Enter total portfolio after market return (before discretionary withdrawal): "))
nper = int(input("Enter number of total periods for discretionary withdrawal: "))

# --- CAPE-based expected return inputs for amortization ---
pe = float(input("Enter the CAPE ratio: "))
target_pe = float(input("Enter the Target CAPE ratio: "))
earnings_growth = float(input("Enter the expected earnings growth: "))

# --- Step 0: Compute expected return per period for amortization ---
valuation_change = (target_pe / pe) ** (1/10) - 1
annual_expected_return = (1 / pe) + earnings_growth + valuation_change
period_expected_return = (1 + annual_expected_return) ** (1 / 24) - 1  # semi-monthly

# --- Step 1: Withdraw essentials from liability ---
liability_portion -= essential_withdrawal

# --- Step 2: Compute actual realized return over period (net of essentials) ---
actual_return = (total_portfolio_after_market - (total_portfolio_start - essential_withdrawal)) / (total_portfolio_start - essential_withdrawal)

# --- Step 3: Apply actual return to liability portion ---
liability_portion *= (1 + actual_return)

# --- Step 4: Compute updated surplus portion ---
surplus_portion = total_portfolio_after_market - liability_portion

# --- Step 5: Amortization-based withdrawal from surplus using expected return ---
amort_payment = pmt(rate=period_expected_return, nper=nper, pv=surplus_portion)
amort_payment = -amort_payment  # make positive
surplus_portion -= amort_payment

# --- Step 6: Compute final total portfolio ---
total_portfolio_final = liability_portion + surplus_portion

# --- Output ---
print(f"\nEssential withdrawal: ${essential_withdrawal:,.2f}")
print(f"Discretionary withdrawal (amortized): ${amort_payment:,.2f}")
print(f"Updated liability portion: ${liability_portion:,.2f}")
print(f"Updated surplus portion: ${surplus_portion:,.2f}")
print(f"Final total portfolio: ${total_portfolio_final:,.2f}")
print(f"Actual realized return this period: {actual_return*100:.4f}%")
print(f"Semi-monthly expected return used for amortization: {period_expected_return*100:.4f}%")
print(f"Annual expected return: {annual_expected_return*100:.2f}%")

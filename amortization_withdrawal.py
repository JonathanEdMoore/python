def pmt(rate, nper, pv, fv=0, when=0):
    """
    Recreate Excel's PMT function.

    Parameters:
    rate -- interest rate per period
    nper -- number of total periods
    pv -- present value (amount borrowed/invested)
    fv -- future value (default 0)
    when -- 0 for end of period, 1 for beginning (default 0)

    Returns:
    Payment amount per period
    """
    if rate == 0:
        return -(pv + fv) / nper

    factor = (1 + rate)**nper
    return -(pv * factor + fv) / ((1 + rate * when) * (factor - 1) / rate)

# --- User Inputs ---
total_portfolio = float(input("Enter total portfolio value: "))
liability_portion = float(input("Enter liability portion: "))
essential_withdrawal = float(input("Enter essential withdrawal for this period: "))

# CAPE-based expected return inputs
pe = float(input("Enter the CAPE ratio: "))
target_pe = float(input("Enter the Target CAPE ratio: "))
earnings_growth = float(input("Enter the expected earnings growth: "))
nper = int(input("Enter the number of periods for discretionary withdrawal: "))

# --- Step 0: Compute per-period return from CAPE ---
valuation_change = (target_pe / pe) ** (1/10) - 1
annual_rate = (1 / pe) + earnings_growth + valuation_change
period_return = (1 + annual_rate) ** (1 / 24) - 1  # semi-monthly

# --- Step 1: Calculate surplus portion ---
surplus_portion = total_portfolio - liability_portion

# --- Step 2: Withdraw essentials from liability ---
liability_portion -= essential_withdrawal

# --- Step 3: Apply market return to both portions ---
liability_portion *= (1 + period_return)
surplus_portion *= (1 + period_return)

# --- Step 4: Amortization-based withdrawal from surplus ---
amort_payment = pmt(rate=period_return, nper=nper, pv=surplus_portion)
amort_payment = -amort_payment  # make positive
surplus_portion -= amort_payment

# --- Step 5: Calculate updated total portfolio ---
total_portfolio = liability_portion + surplus_portion

# --- Output ---
print(f"\nEssential withdrawal: ${essential_withdrawal:,.2f}")
print(f"Discretionary withdrawal: ${amort_payment:,.2f}")
print(f"Updated liability portion: ${liability_portion:,.2f}")
print(f"Updated surplus portion: ${surplus_portion:,.2f}")
print(f"Updated total portfolio: ${total_portfolio:,.2f}")
print(f"Semi-monthly period return used: {period_return*100:.4f}%")
print(f"Annualized expected return from CAPE: {annual_rate*100:.2f}%")

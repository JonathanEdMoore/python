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

pe = float(input("Enter the CAPE ratio: "))
target_pe = float(input("Enter the Target CAPE ratio: "))
earnings_growth = float(input("Enter the expected earnings growth: "))
nper = int(input("Enter the number of periods: "))
pv = float(input("Enter the present value: "))

valuation_change = (target_pe/pe) ** (1/10) - 1
annual_rate = (1/pe) + earnings_growth + valuation_change
rate = (1 + annual_rate) ** (1/24) - 1

payment = pmt(rate, nper, pv)
print(f"\nPayment per period: ${payment:,.2f}")
print(f"Annual Return: {annual_rate * 100:.2f}%")

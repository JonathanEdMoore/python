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

annual_rate = float(input("Enter the expected real return (e.g. 0.05 for 5%): "))
nper = int(input("Enter the number of periods: "))
pv = float(input("Enter the present value: "))

rate = (1 + annual_rate) ** (1/24) - 1

payment = pmt(rate, nper, pv)
print(f"\nPayment per period: ${payment:,.2f}")
print(f"Annual Return: {annual_rate * 100:.2f}%")

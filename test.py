import yfinance as yf

# Define the stock ticker
ticker = "VT"  # Example: VT for Vanguard Total World Stock ETF

# Fetch historical data for the stock
stock = yf.Ticker(ticker)
data = stock.history(period="max")

# Calculate the expected price return (based on historical price changes)
data['Price Return'] = data['Close'].pct_change()
expected_price_return = data['Price Return'].mean() * 252  # Annualize the return assuming 252 trading days

# Resample dividend data to get annual dividends
dividends = stock.dividends
annual_dividends = dividends.resample('Y').sum()  # Sum dividends per year

# Calculate average closing price per year
annual_prices = data['Close'].resample('Y').mean()

# Calculate annual dividend yields
annual_dividend_yields = annual_dividends / annual_prices

# Average annual dividend yield
average_dividend_yield = annual_dividend_yields.mean()

# Calculate the total expected return
expected_total_return = expected_price_return + average_dividend_yield

print(f"Expected Annual Price Return: {expected_price_return:.2%}")
print(f"Average Annual Dividend Yield: {average_dividend_yield:.2%}")
print(f"Total Expected Return: {expected_total_return:.2%}")

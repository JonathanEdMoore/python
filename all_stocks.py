import json
import yfinance as yf
import pandas as pd
import time

# Load the JSON data
with open("vt.json", "r") as file:
    data = json.load(file)

# Extract the first 5 holdings from the data
holdings = data.get("holding", [])

# Prepare lists to store tickers and market caps
tickers_list = []
market_caps = []

# Loop through each holding and create a Ticker object using ISIN
for holding in holdings:
    isin = holding.get("isin")
    
    if isin:  # Ensure ISIN is available
        ticker_yahoo = yf.Ticker(isin)  # Create the Ticker object for ISIN
        market_cap = ticker_yahoo.info.get("marketCap", "No Data")
        
        # Append ticker and market cap to the lists
        tickers_list.append(ticker_yahoo.ticker)
        market_caps.append(market_cap)
        
    time.sleep(1)  # Sleep to avoid hitting rate limits

# Create a DataFrame to store the tickers and market caps
df = pd.DataFrame({
    "Ticker": tickers_list,
    "Market Cap": market_caps
})

# Save the data to a CSV file
df.to_csv("market_caps_first_5.csv", index=False)

print("Market cap data for the first 5 stocks saved to market_caps_first_5.csv")

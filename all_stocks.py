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

# Loop through each holding and create a Ticker object using ISIN
for holding in holdings:
    isin = holding.get("isin")
    
    if isin:  # Ensure ISIN is available
        ticker_yahoo = yf.Ticker(isin)  # Create the Ticker object for ISIN
        
        # Append ticker and market cap to the lists
        tickers_list.append(ticker_yahoo.ticker)
        
    time.sleep(1)  # Sleep to avoid hitting rate limits

# Create a DataFrame to store the tickers and market caps
df = pd.DataFrame({
    "Ticker": tickers_list,
})

# Save the data to a CSV file
df.to_csv("stocks_ordered_by_market_cap.csv", index=False)

print("Stocks ordered by Market Cap saved to stocks_ordered_by_market_cap.csv")

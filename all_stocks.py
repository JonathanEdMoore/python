import json
import yfinance as yf
import pandas as pd
import time
from requests.exceptions import Timeout

# Load the JSON data
with open("vt.json", "r") as file:
    data = json.load(file)

# Extract holdings from the data
holdings = data.get("holding", [])

# Prepare a list to store the tickers
tickers_list = []

# Function to handle retries and rate-limiting
def get_ticker_yahoo(isin):
    retries = 3  # Number of retries on failure
    for attempt in range(retries):
        try:
            ticker_yahoo = yf.Ticker(isin)  # Create the Ticker object for ISIN
            return ticker_yahoo
        except Timeout as e:
            print(f"Timeout error for {isin}. Retrying... ({attempt+1}/{retries})")
            time.sleep(5)  # Wait before retrying
        except Exception as e:
            print(f"Error for {isin}: {e}")
            break  # Stop retrying on other errors
    return None  # Return None if all retries fail

# Loop through each holding and create a Ticker object using ISIN
for holding in holdings:
    isin = holding.get("isin")
    
    if isin:  # Ensure that ISIN is available
        ticker_yahoo = get_ticker_yahoo(isin)  # Get the Ticker object for ISIN
        if ticker_yahoo:
            print(f"Adding ticker: {ticker_yahoo.ticker}")
            tickers_list.append(ticker_yahoo.ticker)  # Add to the tickers list
        time.sleep(1)  # Sleep to avoid hitting rate limits

# Print the list of tickers
print(tickers_list)

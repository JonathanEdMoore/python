import yfinance as yf
import pandas as pd

def calculate_correlation(stock1, stock2, start_date='2020-01-01', end_date='2025-01-01'):
    # Fetch the historical data for both stocks
    data1 = yf.download(stock1, start=start_date, end=end_date)['Close']
    data2 = yf.download(stock2, start=start_date, end=end_date)['Close']
    
    # Calculate daily returns for both stocks
    returns1 = data1.pct_change().dropna()
    returns2 = data2.pct_change().dropna()
    
    # Combine the two series into one DataFrame
    combined_data = pd.concat([returns1, returns2], axis=1)
    combined_data.columns = [stock1, stock2]
    
    # Calculate the correlation between the returns
    correlation = combined_data.corr().iloc[0, 1]
    
    print(f"The correlation between {stock1} and {stock2} is: {correlation:.4f}")
    
    return correlation

# Accept user input for stock tickers
stock1 = input("Enter the ticker symbol for the first stock (e.g., AAPL): ").upper()
stock2 = input("Enter the ticker symbol for the second stock (e.g., MSFT): ").upper()

# Example usage with user input
calculate_correlation(stock1, stock2)

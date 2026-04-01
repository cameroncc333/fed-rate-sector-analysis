"""
Fed Rate Sector Analysis — Data Collection
Cameron Camarotti | github.com/cameroncc333

Pulls historical daily closing prices for all 11 S&P 500 sector ETFs
using the Yahoo Finance API (yfinance library).

Usage:
    python data_collection.py
    
This will download sector price data and save it to data/sector_prices.csv
"""

import pandas as pd
import os
from datetime import datetime

try:
    import yfinance as yf
    HAS_YFINANCE = True
except ImportError:
    HAS_YFINANCE = False

from fomc_dates import SECTOR_ETFS, FOMC_DECISIONS


def download_sector_data(start_date="2021-01-01", end_date=None):
    """
    Download daily closing prices for all S&P 500 sector ETFs.
    
    We start from 2021 to have pre-hiking-cycle data for comparison.
    
    Args:
        start_date: Start date for price history (YYYY-MM-DD)
        end_date: End date (defaults to today)
    
    Returns:
        DataFrame with dates as index and sector ETF tickers as columns
    """
    if not HAS_YFINANCE:
        print("  ERROR: yfinance not installed.")
        print("  Run: pip install yfinance")
        print("")
        print("  Loading sample data instead...")
        return load_sample_data()
    
    if end_date is None:
        end_date = datetime.today().strftime("%Y-%m-%d")
    
    tickers = list(SECTOR_ETFS.keys())
    print(f"  Downloading data for {len(tickers)} sector ETFs...")
    print(f"  Date range: {start_date} to {end_date}")
    print(f"  Tickers: {', '.join(tickers)}")
    print()
    
    # Download all tickers at once for efficiency
    data = yf.download(tickers, start=start_date, end=end_date)["Close"]
    
    # Handle single ticker edge case
    if isinstance(data, pd.Series):
        data = data.to_frame()
    
    print(f"\n  Downloaded {len(data)} trading days of data")
    print(f"  Date range: {data.index[0].strftime('%Y-%m-%d')} to {data.index[-1].strftime('%Y-%m-%d')}")
    
    return data


def load_sample_data():
    """
    Load sample data from CSV if yfinance is not available.
    This allows the analysis code to run without an internet connection.
    """
    sample_path = os.path.join("data", "sector_prices.csv")
    if os.path.exists(sample_path):
        data = pd.read_csv(sample_path, index_col=0, parse_dates=True)
        print(f"  Loaded {len(data)} rows from {sample_path}")
        return data
    else:
        print("  No sample data available. Please install yfinance:")
        print("  pip install yfinance")
        return None


def save_data(data, filepath="data/sector_prices.csv"):
    """Save downloaded data to CSV for offline use."""
    os.makedirs(os.path.dirname(filepath), exist_ok=True)
    data.to_csv(filepath)
    print(f"  Saved to {filepath}")


def get_fomc_dataframe():
    """
    Convert FOMC decisions list to a pandas DataFrame.
    
    Returns:
        DataFrame with columns: date, action, change_bps, new_rate
    """
    df = pd.DataFrame(FOMC_DECISIONS, 
                       columns=["date", "action", "change_bps", "new_rate"])
    df["date"] = pd.to_datetime(df["date"])
    return df


def print_data_summary(price_data, fomc_data):
    """Print a summary of the collected data."""
    print("=" * 60)
    print("  DATA COLLECTION SUMMARY")
    print("=" * 60)
    
    print(f"\n  SECTOR ETF PRICE DATA")
    print(f"    Trading days:     {len(price_data)}")
    print(f"    Sectors tracked:  {len(price_data.columns)}")
    print(f"    Date range:       {price_data.index[0].strftime('%Y-%m-%d')} to "
          f"{price_data.index[-1].strftime('%Y-%m-%d')}")
    print(f"    Missing values:   {price_data.isnull().sum().sum()}")
    
    print(f"\n  FOMC DECISIONS")
    print(f"    Total decisions:  {len(fomc_data)}")
    print(f"    Rate hikes:       {len(fomc_data[fomc_data['action'] == 'hike'])}")
    print(f"    Rate cuts:        {len(fomc_data[fomc_data['action'] == 'cut'])}")
    print(f"    Holds:            {len(fomc_data[fomc_data['action'] == 'hold'])}")
    print(f"    Date range:       {fomc_data['date'].min().strftime('%Y-%m-%d')} to "
          f"{fomc_data['date'].max().strftime('%Y-%m-%d')}")
    
    print(f"\n  SECTORS TRACKED")
    for ticker, name in SECTOR_ETFS.items():
        latest = price_data[ticker].dropna().iloc[-1] if ticker in price_data.columns else "N/A"
        print(f"    {ticker:5s} — {name:30s} (Latest: ${latest:.2f})" if isinstance(latest, float) 
              else f"    {ticker:5s} — {name:30s} (No data)")
    
    print("=" * 60)


if __name__ == "__main__":
    print("\n  FED RATE SECTOR ANALYSIS — DATA COLLECTION")
    print("  Cameron Camarotti | github.com/cameroncc333\n")
    
    # Download sector prices
    price_data = download_sector_data()
    
    if price_data is not None:
        # Save to CSV
        save_data(price_data)
        
        # Load FOMC data
        fomc_data = get_fomc_dataframe()
        
        # Print summary
        print_data_summary(price_data, fomc_data)
        
        print(f"\n  Data collection complete. Run analysis.py next.")

"""
Fed Rate Sector Analysis — Core Analysis
Cameron Camarotti | github.com/cameroncc333

Calculates sector-level returns over 30, 60, and 90-day windows
following each FOMC rate decision. Identifies which sectors are
most and least sensitive to monetary policy changes.

This is the analytical core of the project — answering the question:
"When the Fed changes rates, which parts of the economy feel it most?"
"""

import pandas as pd
import numpy as np
import os
from fomc_dates import SECTOR_ETFS, RETURN_WINDOWS
from data_collection import download_sector_data, load_sample_data, get_fomc_dataframe


def calculate_sector_returns(price_data, fomc_data, windows=RETURN_WINDOWS):
    """
    For each FOMC decision, calculate how each sector performed
    over the following 30, 60, and 90 trading days.
    
    Method:
    1. Find the closest trading day to each FOMC decision date
    2. Get the closing price on that day (or next trading day)
    3. Get the closing price N trading days later
    4. Calculate percentage return: (P_end - P_start) / P_start × 100
    
    Args:
        price_data: DataFrame of daily sector ETF prices
        fomc_data: DataFrame of FOMC decisions
        windows: List of trading-day windows to analyze [30, 60, 90]
    
    Returns:
        Dictionary of DataFrames, one per window, with sectors as columns
        and FOMC dates as rows
    """
    results = {}
    
    for window in windows:
        window_results = []
        
        for _, decision in fomc_data.iterrows():
            decision_date = decision["date"]
            action = decision["action"]
            change = decision["change_bps"]
            
            # Find the nearest trading day on or after the decision
            valid_dates = price_data.index[price_data.index >= decision_date]
            if len(valid_dates) == 0:
                continue
            start_date = valid_dates[0]
            
            # Find the start position in the index
            start_idx = price_data.index.get_loc(start_date)
            
            # Check if we have enough future data
            if start_idx + window >= len(price_data):
                continue
            
            end_date = price_data.index[start_idx + window]
            
            # Calculate returns for each sector
            row = {
                "decision_date": decision_date,
                "action": action,
                "change_bps": change,
                "rate_after": decision["new_rate"],
            }
            
            for ticker in SECTOR_ETFS.keys():
                if ticker in price_data.columns:
                    start_price = price_data.loc[start_date, ticker]
                    end_price = price_data.loc[end_date, ticker]
                    
                    if pd.notna(start_price) and pd.notna(end_price) and start_price > 0:
                        pct_return = ((end_price - start_price) / start_price) * 100
                        row[ticker] = round(pct_return, 2)
                    else:
                        row[ticker] = np.nan
            
            window_results.append(row)
        
        results[window] = pd.DataFrame(window_results)
    
    return results


def analyze_by_action(return_data, windows=RETURN_WINDOWS):
    """
    Separate analysis by decision type: hikes, cuts, and holds.
    
    For each action type and each window, calculate:
    - Mean sector return
    - Median sector return
    - Best performing sector
    - Worst performing sector
    
    Args:
        return_data: Dictionary of DataFrames from calculate_sector_returns
        windows: List of windows analyzed
    
    Returns:
        Dictionary with analysis broken down by action type
    """
    analysis = {}
    tickers = list(SECTOR_ETFS.keys())
    
    for action in ["hike", "cut", "hold"]:
        action_analysis = {}
        
        for window in windows:
            df = return_data[window]
            action_df = df[df["action"] == action]
            
            if len(action_df) == 0:
                continue
            
            # Calculate mean return per sector
            sector_means = {}
            sector_medians = {}
            
            for ticker in tickers:
                if ticker in action_df.columns:
                    returns = action_df[ticker].dropna()
                    if len(returns) > 0:
                        sector_means[ticker] = round(returns.mean(), 2)
                        sector_medians[ticker] = round(returns.median(), 2)
            
            if sector_means:
                best_sector = max(sector_means, key=sector_means.get)
                worst_sector = min(sector_means, key=sector_means.get)
                
                action_analysis[window] = {
                    "num_decisions": len(action_df),
                    "mean_returns": sector_means,
                    "median_returns": sector_medians,
                    "best_sector": (best_sector, SECTOR_ETFS[best_sector], sector_means[best_sector]),
                    "worst_sector": (worst_sector, SECTOR_ETFS[worst_sector], sector_means[worst_sector]),
                    "avg_all_sectors": round(np.mean(list(sector_means.values())), 2),
                }
        
        analysis[action] = action_analysis
    
    return analysis


def rank_sector_sensitivity(return_data, window=60):
    """
    Rank sectors by their sensitivity to rate changes.
    
    Sensitivity = absolute difference in average return between
    hike periods and cut periods. Higher sensitivity means the
    sector's performance changes more based on Fed action.
    
    Args:
        return_data: Dictionary of DataFrames
        window: Which window to use for ranking (default 60 days)
    
    Returns:
        List of (ticker, name, sensitivity_score, hike_avg, cut_avg) tuples
        sorted by sensitivity descending
    """
    df = return_data[window]
    tickers = list(SECTOR_ETFS.keys())
    
    hike_df = df[df["action"] == "hike"]
    cut_df = df[df["action"] == "cut"]
    
    sensitivities = []
    
    for ticker in tickers:
        if ticker not in df.columns:
            continue
            
        hike_returns = hike_df[ticker].dropna()
        cut_returns = cut_df[ticker].dropna()
        
        if len(hike_returns) > 0 and len(cut_returns) > 0:
            hike_avg = hike_returns.mean()
            cut_avg = cut_returns.mean()
            sensitivity = abs(cut_avg - hike_avg)
            
            sensitivities.append((
                ticker,
                SECTOR_ETFS[ticker],
                round(sensitivity, 2),
                round(hike_avg, 2),
                round(cut_avg, 2)
            ))
    
    # Sort by sensitivity (most sensitive first)
    sensitivities.sort(key=lambda x: x[2], reverse=True)
    return sensitivities


def print_analysis_report(analysis, sensitivities):
    """Print a comprehensive analysis report."""
    
    print("=" * 70)
    print("  FEDERAL RESERVE RATE DECISIONS — S&P 500 SECTOR IMPACT ANALYSIS")
    print("  Cameron Camarotti | github.com/cameroncc333")
    print("=" * 70)
    
    for action in ["hike", "cut", "hold"]:
        action_data = analysis.get(action, {})
        if not action_data:
            continue
            
        action_label = {"hike": "RATE HIKES", "cut": "RATE CUTS", "hold": "RATE HOLDS"}[action]
        
        print(f"\n{'─' * 70}")
        print(f"  {action_label}")
        print(f"{'─' * 70}")
        
        for window in sorted(action_data.keys()):
            data = action_data[window]
            print(f"\n  {window}-Day Window ({data['num_decisions']} decisions)")
            print(f"  Average across all sectors: {data['avg_all_sectors']:+.2f}%")
            
            best = data["best_sector"]
            worst = data["worst_sector"]
            print(f"  Best sector:  {best[0]} ({best[1]}) → {best[2]:+.2f}%")
            print(f"  Worst sector: {worst[0]} ({worst[1]}) → {worst[2]:+.2f}%")
            
            print(f"\n  All sectors (mean {window}-day return):")
            sorted_returns = sorted(data["mean_returns"].items(), 
                                   key=lambda x: x[1], reverse=True)
            for ticker, ret in sorted_returns:
                name = SECTOR_ETFS.get(ticker, ticker)
                bar = "█" * max(1, int(abs(ret) * 2))
                direction = "+" if ret >= 0 else ""
                print(f"    {ticker:5s} {name:28s} {direction}{ret:.2f}%  {bar}")
    
    # Sensitivity rankings
    print(f"\n{'─' * 70}")
    print(f"  SECTOR SENSITIVITY RANKINGS (60-Day Window)")
    print(f"  Sensitivity = |avg return after cuts - avg return after hikes|")
    print(f"{'─' * 70}")
    
    for rank, (ticker, name, sensitivity, hike_avg, cut_avg) in enumerate(sensitivities, 1):
        print(f"\n  #{rank} {ticker} — {name}")
        print(f"     Sensitivity Score:     {sensitivity:.2f}")
        print(f"     Avg return after hikes: {hike_avg:+.2f}%")
        print(f"     Avg return after cuts:  {cut_avg:+.2f}%")
    
    if sensitivities:
        most = sensitivities[0]
        least = sensitivities[-1]
        print(f"\n  MOST SENSITIVE:  {most[0]} ({most[1]}) — score {most[2]}")
        print(f"  LEAST SENSITIVE: {least[0]} ({least[1]}) — score {least[2]}")
    
    print(f"\n{'=' * 70}")
    print(f"  METHODOLOGY NOTES")
    print(f"{'=' * 70}")
    print(f"  - Returns calculated from FOMC decision date to N trading days later")
    print(f"  - Sector returns are total price returns (dividends not included)")
    print(f"  - Analysis covers FOMC decisions from 2022-2025")
    print(f"  - Sensitivity measures how differently a sector responds to hikes vs cuts")
    print(f"  - Higher sensitivity = sector performance depends more on Fed policy")
    print(f"{'=' * 70}")


if __name__ == "__main__":
    print("\n  FED RATE SECTOR ANALYSIS — RUNNING ANALYSIS")
    print("  Cameron Camarotti | github.com/cameroncc333\n")
    
    # Load data
    print("  Loading sector price data...")
    price_data = download_sector_data()
    
    if price_data is None:
        print("  ERROR: Could not load price data. Run data_collection.py first.")
        exit(1)
    
    fomc_data = get_fomc_dataframe()
    
    # Calculate returns
    print("  Calculating sector returns after each FOMC decision...")
    return_data = calculate_sector_returns(price_data, fomc_data)
    
    # Analyze by action type
    print("  Analyzing by decision type (hike/cut/hold)...")
    analysis = analyze_by_action(return_data)
    
    # Rank sensitivity
    print("  Ranking sector sensitivity...")
    sensitivities = rank_sector_sensitivity(return_data)
    
    # Print report
    print_analysis_report(analysis, sensitivities)
    
    # Save results
    os.makedirs("output", exist_ok=True)
    for window, df in return_data.items():
        filepath = f"output/sector_returns_{window}day.csv"
        df.to_csv(filepath, index=False)
        print(f"  Saved: {filepath}")
    
    print(f"\n  Analysis complete.")

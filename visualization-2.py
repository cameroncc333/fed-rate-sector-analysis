"""
Fed Rate Sector Analysis — Visualization
Cameron Camarotti | github.com/cameroncc333

Generates publication-quality charts showing how different S&P 500
sectors respond to Federal Reserve rate decisions.
"""

import numpy as np
import pandas as pd
import os

try:
    import matplotlib.pyplot as plt
    import matplotlib.ticker as mticker
    HAS_MATPLOTLIB = True
except ImportError:
    HAS_MATPLOTLIB = False

from fomc_dates import SECTOR_ETFS, RETURN_WINDOWS
from data_collection import download_sector_data, get_fomc_dataframe
from analysis import calculate_sector_returns, analyze_by_action, rank_sector_sensitivity


def set_style():
    """Set consistent chart styling."""
    if not HAS_MATPLOTLIB:
        return
    plt.rcParams.update({
        "figure.facecolor": "white",
        "axes.facecolor": "#f8f9fa",
        "axes.edgecolor": "#cccccc",
        "axes.grid": True,
        "grid.alpha": 0.3,
        "font.family": "sans-serif",
        "font.size": 11,
        "axes.titlesize": 14,
        "axes.titleweight": "bold",
    })


def plot_hike_vs_cut_comparison(analysis, window=60, 
                                 save_path="output/hike_vs_cut_comparison.png"):
    """
    Side-by-side bar chart comparing sector performance 
    after rate hikes vs rate cuts.
    """
    if not HAS_MATPLOTLIB:
        print("  matplotlib not installed. Skipping chart generation.")
        return
        
    set_style()
    
    hike_data = analysis.get("hike", {}).get(window, {})
    cut_data = analysis.get("cut", {}).get(window, {})
    
    if not hike_data or not cut_data:
        print(f"  Insufficient data for {window}-day hike vs cut comparison")
        return
    
    tickers = [t for t in SECTOR_ETFS.keys() 
               if t in hike_data["mean_returns"] and t in cut_data["mean_returns"]]
    names = [SECTOR_ETFS[t] for t in tickers]
    hike_returns = [hike_data["mean_returns"][t] for t in tickers]
    cut_returns = [cut_data["mean_returns"][t] for t in tickers]
    
    # Sort by the difference (most sensitive first)
    sorted_idx = sorted(range(len(tickers)), 
                        key=lambda i: cut_returns[i] - hike_returns[i], reverse=True)
    names = [names[i] for i in sorted_idx]
    hike_returns = [hike_returns[i] for i in sorted_idx]
    cut_returns = [cut_returns[i] for i in sorted_idx]
    
    fig, ax = plt.subplots(figsize=(12, 7))
    
    x = np.arange(len(names))
    width = 0.35
    
    bars1 = ax.bar(x - width/2, hike_returns, width, label="After Rate Hikes",
                   color="#E74C3C", edgecolor="white", alpha=0.85)
    bars2 = ax.bar(x + width/2, cut_returns, width, label="After Rate Cuts",
                   color="#27AE60", edgecolor="white", alpha=0.85)
    
    ax.axhline(y=0, color="#333333", linewidth=0.8, linestyle="-")
    ax.set_ylabel(f"Average {window}-Day Return (%)")
    ax.set_title(f"S&P 500 Sector Performance: Rate Hikes vs Rate Cuts ({window}-Day Window)")
    ax.set_xticks(x)
    ax.set_xticklabels(names, rotation=45, ha="right", fontsize=9)
    ax.legend(loc="upper right")
    ax.yaxis.set_major_formatter(mticker.FormatStrFormatter("%+.1f%%"))
    
    plt.tight_layout()
    os.makedirs(os.path.dirname(save_path), exist_ok=True)
    plt.savefig(save_path, dpi=150, bbox_inches="tight")
    print(f"  Saved: {save_path}")
    plt.close()


def plot_sensitivity_rankings(sensitivities, save_path="output/sensitivity_rankings.png"):
    """
    Horizontal bar chart ranking sectors by their sensitivity
    to Fed rate decisions.
    """
    if not HAS_MATPLOTLIB:
        return
        
    set_style()
    fig, ax = plt.subplots(figsize=(11, 7))
    
    names = [f"{s[0]} — {s[1]}" for s in sensitivities]
    scores = [s[2] for s in sensitivities]
    
    colors = plt.cm.RdYlGn_r(np.linspace(0.2, 0.8, len(names)))
    
    bars = ax.barh(names, scores, color=colors, edgecolor="white", height=0.6)
    
    for bar, score in zip(bars, scores):
        ax.text(bar.get_width() + 0.2, bar.get_y() + bar.get_height()/2,
                f"{score:.1f}", va="center", fontsize=10, fontweight="bold")
    
    ax.set_xlabel("Sensitivity Score (|avg return after cuts − avg return after hikes|)")
    ax.set_title("Sector Sensitivity to Federal Reserve Rate Decisions\n"
                 "Higher score = sector performance depends more on Fed policy")
    ax.invert_yaxis()
    
    plt.tight_layout()
    os.makedirs(os.path.dirname(save_path), exist_ok=True)
    plt.savefig(save_path, dpi=150, bbox_inches="tight")
    print(f"  Saved: {save_path}")
    plt.close()


def plot_sector_heatmap(return_data, action="hike", 
                        save_path="output/sector_heatmap_hikes.png"):
    """
    Heatmap showing each sector's return after each individual
    FOMC decision. Rows = decisions, columns = sectors.
    """
    if not HAS_MATPLOTLIB:
        return
        
    set_style()
    
    window = 60
    df = return_data[window]
    action_df = df[df["action"] == action].copy()
    
    if len(action_df) == 0:
        print(f"  No {action} decisions found for heatmap")
        return
    
    tickers = [t for t in SECTOR_ETFS.keys() if t in action_df.columns]
    names = [SECTOR_ETFS[t] for t in tickers]
    
    # Create matrix
    matrix = action_df[tickers].values
    dates = action_df["decision_date"].dt.strftime("%Y-%m-%d").values
    
    fig, ax = plt.subplots(figsize=(14, max(6, len(dates) * 0.5)))
    
    im = ax.imshow(matrix, cmap="RdYlGn", aspect="auto",
                   vmin=-15, vmax=15)
    
    ax.set_xticks(range(len(names)))
    ax.set_xticklabels(names, rotation=45, ha="right", fontsize=9)
    ax.set_yticks(range(len(dates)))
    ax.set_yticklabels(dates, fontsize=8)
    
    # Add value labels
    for i in range(len(dates)):
        for j in range(len(tickers)):
            val = matrix[i, j]
            if not np.isnan(val):
                color = "white" if abs(val) > 8 else "black"
                ax.text(j, i, f"{val:.1f}", ha="center", va="center",
                       fontsize=7, color=color)
    
    action_label = {"hike": "Rate Hikes", "cut": "Rate Cuts", "hold": "Rate Holds"}[action]
    ax.set_title(f"Sector Returns (60-Day) After Each FOMC {action_label}\n"
                 f"Green = positive return, Red = negative return")
    
    plt.colorbar(im, ax=ax, label="Return (%)", shrink=0.8)
    plt.tight_layout()
    os.makedirs(os.path.dirname(save_path), exist_ok=True)
    plt.savefig(save_path, dpi=150, bbox_inches="tight")
    print(f"  Saved: {save_path}")
    plt.close()


def plot_rate_timeline(fomc_data, save_path="output/rate_timeline.png"):
    """Plot the federal funds rate over time with hike/cut markers."""
    if not HAS_MATPLOTLIB:
        return
        
    set_style()
    fig, ax = plt.subplots(figsize=(12, 5))
    
    dates = fomc_data["date"]
    rates = fomc_data["new_rate"]
    actions = fomc_data["action"]
    
    ax.plot(dates, rates, color="#2E75B6", linewidth=2, zorder=2)
    
    for date, rate, action in zip(dates, rates, actions):
        if action == "hike":
            ax.scatter(date, rate, color="#E74C3C", s=60, zorder=3, 
                      edgecolors="white", linewidth=1)
        elif action == "cut":
            ax.scatter(date, rate, color="#27AE60", s=60, zorder=3,
                      edgecolors="white", linewidth=1)
    
    ax.scatter([], [], color="#E74C3C", s=60, label="Rate Hike", edgecolors="white")
    ax.scatter([], [], color="#27AE60", s=60, label="Rate Cut", edgecolors="white")
    ax.scatter([], [], color="#2E75B6", s=30, label="Hold", edgecolors="white")
    
    ax.set_xlabel("Date")
    ax.set_ylabel("Federal Funds Rate (%)")
    ax.set_title("Federal Funds Rate — FOMC Decisions (2022–2025)")
    ax.legend(loc="upper left")
    ax.yaxis.set_major_formatter(mticker.FormatStrFormatter("%.2f%%"))
    
    plt.tight_layout()
    os.makedirs(os.path.dirname(save_path), exist_ok=True)
    plt.savefig(save_path, dpi=150, bbox_inches="tight")
    print(f"  Saved: {save_path}")
    plt.close()


if __name__ == "__main__":
    print("\n  FED RATE SECTOR ANALYSIS — GENERATING VISUALIZATIONS")
    print("  Cameron Camarotti | github.com/cameroncc333\n")
    
    if not HAS_MATPLOTLIB:
        print("  ERROR: matplotlib not installed.")
        print("  Run: pip install matplotlib")
        exit(1)
    
    # Load data
    print("  Loading data...")
    price_data = download_sector_data()
    
    if price_data is None:
        print("  ERROR: No price data. Run data_collection.py first.")
        exit(1)
    
    fomc_data = get_fomc_dataframe()
    
    # Run analysis
    print("  Running analysis...")
    return_data = calculate_sector_returns(price_data, fomc_data)
    analysis = analyze_by_action(return_data)
    sensitivities = rank_sector_sensitivity(return_data)
    
    # Generate all charts
    print("  Generating charts...\n")
    
    plot_rate_timeline(fomc_data)
    plot_hike_vs_cut_comparison(analysis, window=60)
    plot_sensitivity_rankings(sensitivities)
    plot_sector_heatmap(return_data, action="hike", 
                        save_path="output/sector_heatmap_hikes.png")
    plot_sector_heatmap(return_data, action="cut",
                        save_path="output/sector_heatmap_cuts.png")
    
    print(f"\n  All visualizations saved to /output/")
    print("  Upload chart images to the GitHub repo for the README.")

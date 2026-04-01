# Federal Reserve Rate Decisions — S&P 500 Sector Impact Analysis

## Overview

This project analyzes how Federal Reserve interest rate decisions ripple through different sectors of the stock market. Using historical data from S&P 500 sector ETFs and FOMC meeting records, I calculate sector-level returns over 30, 60, and 90-day windows following each rate decision to identify which sectors are most — and least — sensitive to monetary policy changes.

## Motivation

I built an [8-variable pricing model](https://github.com/cameroncc333/aas-pricing-model) for my company, All Around Services, that optimizes job pricing using calculus-based cost functions. One of those variables — the seasonal demand coefficient (κ) — captures how macroeconomic conditions affect local demand for home services.

That got me thinking about the larger question: how do Federal Reserve policy decisions cascade through the broader economy? When the Fed raises rates, which industries feel it first? Which ones are insulated? How long does the effect take to materialize?

This project extends my quantitative analysis from small business pricing to financial market behavior — applying the same data-driven approach at a different scale.

## Methodology

### Data Sources
- **Sector ETFs:** Historical daily prices for S&P 500 sector ETFs via Yahoo Finance (yfinance)
  - XLK (Technology), XLF (Financials), XLE (Energy), XLV (Healthcare)
  - XLY (Consumer Discretionary), XLP (Consumer Staples), XLI (Industrials)
  - XLB (Materials), XLRE (Real Estate), XLU (Utilities), XLC (Communication Services)
- **FOMC Decisions:** Federal Reserve rate decision dates and magnitudes from public Federal Reserve records (2022–2025)

### Analysis Pipeline
1. Pull historical daily closing prices for all 11 sector ETFs
2. Map each FOMC rate decision date with the decision type (hike, cut, hold)
3. For each decision, calculate sector returns over three windows:
   - **30-day return** — immediate market reaction
   - **60-day return** — medium-term adjustment
   - **90-day return** — longer-term sector rotation
4. Aggregate results across all decisions to identify patterns
5. Separate analysis by decision type (hike vs cut vs hold)
6. Rank sectors by sensitivity to monetary policy
7. Visualize results with heatmaps, comparison charts, and rankings

### Key Questions
- Which sectors gain the most after rate cuts?
- Which sectors suffer the most after rate hikes?
- How does the time window (30 vs 60 vs 90 days) change the picture?
- Are "defensive" sectors (Utilities, Healthcare, Staples) actually defensive?
- How sensitive is Real Estate to rate changes compared to other sectors?

## Project Structure

```
fed-rate-sector-analysis/
│
├── README.md                    # This file
├── fomc_dates.py               # Historical FOMC decision dates, actions, and rates
├── data_collection.py           # Pulls sector ETF data via Yahoo Finance API
├── analysis.py                  # Core analysis — sector returns by window and action type
├── visualization.py             # Heatmaps, comparison charts, sensitivity rankings
├── data/
│   └── sector_prices.csv        # Downloaded sector ETF price history
└── output/
    ├── rate_timeline.png
    ├── hike_vs_cut_comparison.png
    ├── sensitivity_rankings.png
    ├── sector_heatmap_hikes.png
    └── sector_heatmap_cuts.png
```

## How to Run

```bash
# Clone the repository
git clone https://github.com/cameroncc333/fed-rate-sector-analysis.git
cd fed-rate-sector-analysis

# Install dependencies
pip install pandas numpy matplotlib yfinance scipy

# Step 1: Download sector price data
python data_collection.py

# Step 2: Run the analysis
python analysis.py

# Step 3: Generate visualization charts
python visualization.py
```

## Tools & Libraries

- **Python 3**
- **pandas** — data manipulation and time series analysis
- **numpy** — numerical computation
- **matplotlib** — visualization (heatmaps, bar charts, timelines)
- **yfinance** — Yahoo Finance API for historical price data
- **scipy** — statistical analysis

## Connection to Other Work

This project is part of a broader quantitative analysis portfolio:

- **[AAS Pricing Model](https://github.com/cameroncc333/aas-pricing-model)** — 8-variable cost function with Monte Carlo simulation for my home services company
- **[AAS Website](https://github.com/cameroncc333/AAS-Website)** — Source code for allaroundservice.com

The through-line across all three projects: applying mathematical and computational methods to real-world economic questions, from pricing optimization at a local business to monetary policy impacts on national markets.

## Relevance

This analysis is directly relevant to:
- **Federal Reserve Bank of Atlanta** — where I'm applying for the High School Research Internship. The Fed's Research Department studies exactly these economic indicators and market dynamics.
- **AP Macroeconomics** — which I'm taking senior year, covering monetary policy, interest rates, and their economic effects
- **Bloomberg Market Concepts** — Modules 1 (Economic Indicators) and 3 (Fixed Income) cover the same frameworks applied here

## About

**Cameron Camarotti**
- Founder, [All Around Services](https://allaroundserviceatl.com)
- [Facebook](https://www.facebook.com/profile.php?id=61588386760982)
- Junior at Mill Creek High School (Class of 2027)
- 4.1 GPA | 12 AP Courses
- Varsity Football — All-Region Honorable Mention

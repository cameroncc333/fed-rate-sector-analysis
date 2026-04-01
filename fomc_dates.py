"""
Historical FOMC Rate Decisions
Federal Reserve Federal Open Market Committee

Data source: Federal Reserve public records
https://www.federalreserve.gov/monetarypolicy/fomccalendars.htm

Each entry: (date, action, change_bps, new_rate)
- action: "hike", "cut", or "hold"
- change_bps: basis point change (positive = hike, negative = cut, 0 = hold)
- new_rate: federal funds target rate upper bound after decision
"""

FOMC_DECISIONS = [
    # 2022 — Aggressive hiking cycle (inflation fighting)
    ("2022-01-26", "hold", 0, 0.25),
    ("2022-03-16", "hike", 25, 0.50),
    ("2022-05-04", "hike", 50, 1.00),
    ("2022-06-15", "hike", 75, 1.75),
    ("2022-07-27", "hike", 75, 2.50),
    ("2022-09-21", "hike", 75, 3.25),
    ("2022-11-02", "hike", 75, 4.00),
    ("2022-12-14", "hike", 50, 4.50),

    # 2023 — Continued hikes then pause
    ("2023-02-01", "hike", 25, 4.75),
    ("2023-03-22", "hike", 25, 5.00),
    ("2023-05-03", "hike", 25, 5.25),
    ("2023-06-14", "hold", 0, 5.25),
    ("2023-07-26", "hike", 25, 5.50),
    ("2023-09-20", "hold", 0, 5.50),
    ("2023-11-01", "hold", 0, 5.50),
    ("2023-12-13", "hold", 0, 5.50),

    # 2024 — Extended hold then cuts begin
    ("2024-01-31", "hold", 0, 5.50),
    ("2024-03-20", "hold", 0, 5.50),
    ("2024-05-01", "hold", 0, 5.50),
    ("2024-06-12", "hold", 0, 5.50),
    ("2024-07-31", "hold", 0, 5.50),
    ("2024-09-18", "cut", -50, 5.00),
    ("2024-11-07", "cut", -25, 4.75),
    ("2024-12-18", "cut", -25, 4.50),

    # 2025
    ("2025-01-29", "hold", 0, 4.50),
    ("2025-03-19", "hold", 0, 4.50),
    ("2025-05-07", "hold", 0, 4.50),
]


# S&P 500 Sector ETF tickers
SECTOR_ETFS = {
    "XLK": "Technology",
    "XLF": "Financials",
    "XLE": "Energy",
    "XLV": "Healthcare",
    "XLY": "Consumer Discretionary",
    "XLP": "Consumer Staples",
    "XLI": "Industrials",
    "XLB": "Materials",
    "XLRE": "Real Estate",
    "XLU": "Utilities",
    "XLC": "Communication Services",
}

# Analysis windows (trading days after decision)
RETURN_WINDOWS = [30, 60, 90]

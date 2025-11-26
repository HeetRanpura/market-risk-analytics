# Market Risk Analytics (Python + SQL)

A small end-to-end Market Risk Analytics project built with **Python**, **SQLite (SQL)**, and an optional **Streamlit** dashboard.

It demonstrates how to:

- Fetch historical price data from an API (via `yfinance`)
- Store the data in a relational SQL database
- Compute basic **risk and performance metrics**:
  - Daily returns
  - Annualized return and volatility
  - Sharpe ratio
  - 95% Value-at-Risk (VaR)
- Visualize metrics in a simple dashboard

This is designed as a compact project for a **Summer Analyst / Engineering internship**.

---

## Features

1. **API → Database Pipeline**
   - Uses `yfinance` to download 1 year of daily price data.
   - Stores data in a `SQLite` database (`db/market_data.db`).
   - Table: `prices(symbol, date, open, high, low, close, volume)`.

2. **Analytics**
   - Loads data from SQL into `pandas`.
   - Computes for each symbol:
     - Annualized return
     - Annualized volatility
     - Sharpe ratio (risk-adjusted return)
     - 95% historical daily Value-at-Risk (VaR)
   - Computes equal-weighted **portfolio metrics** across multiple symbols.

3. **Dashboard**
   - Built with `streamlit`.
   - Shows:
     - Metrics table for selected symbols
     - Equal-weight portfolio metrics
     - Price history charts

---

## Tech Stack

- **Python**: data fetching and analytics
- **SQLite (SQL)**: lightweight relational database
- **Pandas / NumPy**: data manipulation and statistics
- **yFinance**: historical market data
- **Streamlit**: quick interactive dashboard

---

## Project Structure

```text
market-risk-analytics/
├── README.md
├── requirements.txt
├── .gitignore
├── db/
│   └── market_data.db      # created at runtime
└── src/
    ├── config.py
    ├── init_db.py
    ├── fetch_prices.py
    ├── analytics.py
    ├── run_example.py
    └── dashboard.py

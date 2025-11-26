# src/dashboard.py

import sqlite3

import pandas as pd
import streamlit as st

from config import DB_PATH, DEFAULT_SYMBOLS
from analytics import (
    calculate_metrics_for_symbol,
    calculate_portfolio_metrics,
    calculate_max_sharpe_portfolio,
)


def load_price_history(symbol: str) -> pd.DataFrame:
    conn = sqlite3.connect(DB_PATH)
    df = pd.read_sql_query(
        "SELECT date, close FROM prices WHERE symbol = ? ORDER BY date;",
        conn,
        params=(symbol,),
        parse_dates=["date"],
    )
    conn.close()
    df.set_index("date", inplace=True)
    return df


def main():
    st.title("Market Risk Analytics Dashboard")

    # ----- Sidebar config -----
    st.sidebar.header("Configuration")
    symbols = st.sidebar.multiselect(
        "Select symbols",
        options=DEFAULT_SYMBOLS,
        default=DEFAULT_SYMBOLS,
    )

    if not symbols:
        st.warning("Please select at least one symbol.")
        return

    # ----- Individual metrics -----
    st.subheader("Individual Metrics")

    rows = []
    for sym in symbols:
        try:
            rows.append(calculate_metrics_for_symbol(sym))
        except Exception as e:
            st.error(f"Error for {sym}: {e}")

    if rows:
        st.table(pd.DataFrame(rows))

    # ----- Equal-weight portfolio metrics -----
    st.subheader("Portfolio Metrics (Equal Weight)")
    try:
        portfolio_metrics = calculate_portfolio_metrics(symbols)
        st.json(portfolio_metrics)
    except Exception as e:
        st.error(f"Portfolio error: {e}")

    # ----- Max-Sharpe optimized portfolio -----
    st.subheader("Optimized Portfolio (Max Sharpe)")
    try:
        opt = calculate_max_sharpe_portfolio(symbols, n_portfolios=2000)
        st.write("Max-Sharpe portfolio based on historical data:")
        st.json(opt)
    except Exception as e:
        st.error(f"Optimization error: {e}")

    # ----- Price history chart -----
    st.subheader("Price History")
    selected = st.selectbox("Symbol for price chart", symbols)

    try:
        df_price = load_price_history(selected)
        st.line_chart(df_price["close"])
    except Exception as e:
        st.error(f"Error loading price data: {e}")


if __name__ == "__main__":
    main()

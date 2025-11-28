# src/dashboard.py

import pandas as pd
import sqlite3
import seaborn as sns
import matplotlib.pyplot as plt
import streamlit as st

from config import DEFAULT_SYMBOLS, DB_PATH
from analytics import (
    calculate_metrics_for_symbol,
    calculate_portfolio_metrics,
    calculate_max_drawdown,
    calculate_correlations,
)


def load_price_history(symbol: str) -> pd.DataFrame:
    conn = sqlite3.connect(DB_PATH)
    df = pd.read_sql_query(
        "SELECT date, close FROM prices WHERE symbol=? ORDER BY date ASC",
        conn,
        params=(symbol,),
        parse_dates=["date"]
    )
    conn.close()

    if df.empty:
        raise ValueError(f"No data for symbol {symbol}")

    df.set_index("date", inplace=True)
    return df


def main():
    st.set_page_config(page_title="Market Risk Analytics Dashboard", layout="wide")
    st.title("📈 Market Risk Analytics Dashboard")

    # Sidebar config
    symbols = st.sidebar.multiselect(
        "Select symbols for portfolio",
        options=DEFAULT_SYMBOLS,
        default=DEFAULT_SYMBOLS
    )

    if not symbols:
        st.warning("Please select at least one symbol.")
        st.stop()

    # Individual metrics + max drawdown
    st.subheader("📊 Individual Metrics")
    all_metrics = []
    for sym in symbols:
        metrics = calculate_metrics_for_symbol(sym)
        metrics["max_drawdown"] = calculate_max_drawdown(sym)
        all_metrics.append(metrics)

    st.table(pd.DataFrame(all_metrics))

    # Equal weight portfolio
    st.subheader("📈 Equal-Weight Portfolio Metrics")
    portfolio_metrics = calculate_portfolio_metrics(symbols)
    st.json(portfolio_metrics)

    # Correlation Heatmap
    st.subheader("🧩 Correlation Heatmap")
    corr = calculate_correlations(symbols)

    fig, ax = plt.subplots()
    sns.heatmap(corr, annot=True, cmap="coolwarm", ax=ax)
    st.pyplot(fig)

    # Price chart
    st.subheader("📉 Price History")
    selected = st.selectbox("Select symbol for price chart:", symbols)
    df_price = load_price_history(selected)
    st.line_chart(df_price["close"])


if __name__ == "__main__":
    main()

# src/dashboard.py

import sqlite3

import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
import streamlit as st

from config import DB_PATH, DEFAULT_SYMBOLS
from analytics import (
    calculate_metrics_for_symbol,
    calculate_portfolio_metrics,
    calculate_max_drawdown,
    calculate_correlations,
)


def load_price_history(symbol: str) -> pd.DataFrame:
    """Load close prices for a symbol from the database."""
    conn = sqlite3.connect(DB_PATH)
    df = pd.read_sql_query(
        "SELECT date, close FROM prices WHERE symbol = ? ORDER BY date ASC;",
        conn,
        params=(symbol,),
        parse_dates=["date"],
    )
    conn.close()

    if df.empty:
        raise ValueError(f"No data for symbol {symbol}")

    df.set_index("date", inplace=True)
    return df


def main():
    # ---------- Page setup ----------
    st.set_page_config(
        page_title="Market Risk Analytics Dashboard",
        page_icon="📈",
        layout="wide",
    )

    st.title("📈 Market Risk Analytics Dashboard")
    st.caption(
        "Analyze single-stock and portfolio risk using historical prices, "
        "with metrics like Sharpe, volatility, max drawdown, VaR, and correlations."
    )

    # ---------- Sidebar ----------
    st.sidebar.header("Configuration")

    symbols = st.sidebar.multiselect(
        "Select symbols for analysis",
        options=DEFAULT_SYMBOLS,
        default=DEFAULT_SYMBOLS,
        help="Choose the assets you want to include in the tables, portfolio and heatmap.",
    )

    if not symbols:
        st.warning("Please select at least one symbol from the sidebar.")
        st.stop()

    st.sidebar.markdown("---")
    st.sidebar.write("**Current universe:**")
    st.sidebar.write(", ".join(symbols))

    # ---------- Compute core data once ----------
    # Individual metrics
    symbol_rows = []
    for sym in symbols:
        metrics = calculate_metrics_for_symbol(sym)
        metrics["max_drawdown"] = calculate_max_drawdown(sym)
        symbol_rows.append(metrics)

    symbol_df = pd.DataFrame(symbol_rows)

    # Portfolio metrics (equal weight)
    portfolio_metrics = calculate_portfolio_metrics(symbols)

    # Correlations
    corr_df = calculate_correlations(symbols)

    # ---------- Layout with tabs ----------
    tab_overview, tab_corr, tab_price = st.tabs(
        ["📊 Overview", "🧩 Correlation Heatmap", "📉 Price History"]
    )

    # ===== OVERVIEW TAB =====
    with tab_overview:
        st.subheader("Portfolio Summary")

        col1, col2, col3, col4 = st.columns(4)
        col1.metric(
            "Annual Return",
            f"{portfolio_metrics['annual_return'] * 100:.2f} %",
        )
        col2.metric(
            "Annual Volatility",
            f"{portfolio_metrics['annual_volatility'] * 100:.2f} %",
        )
        col3.metric(
            "Sharpe Ratio",
            f"{portfolio_metrics['sharpe_ratio']:.2f}",
        )
        col4.metric(
            "VaR (95% daily)",
            f"{portfolio_metrics['VaR_95_daily'] * 100:.2f} %",
        )

        st.markdown("---")
        st.subheader("Per-Symbol Risk & Performance Metrics")

        # Slightly nicer column order if present
        display_cols = [
            col
            for col in [
                "symbol",
                "annual_return",
                "annual_volatility",
                "sharpe_ratio",
                "VaR_95_daily",
                "max_drawdown",
            ]
            if col in symbol_df.columns
        ]

        styled_df = (
            symbol_df[display_cols]
            .set_index("symbol")
            .style.format(
                {
                    "annual_return": "{:.4f}",
                    "annual_volatility": "{:.4f}",
                    "sharpe_ratio": "{:.2f}",
                    "VaR_95_daily": "{:.4f}",
                    "max_drawdown": "{:.4f}",
                }
            )
        )
        st.dataframe(styled_df, use_container_width=True)

    # ===== CORRELATION TAB =====
    with tab_corr:
        st.subheader("Correlation Heatmap")

        st.write(
            "This heatmap shows how daily returns of selected symbols move "
            "together. Values close to 1.0 mean they move similarly; values "
            "closer to 0 or negative indicate diversification benefits."
        )

        fig, ax = plt.subplots()
        sns.heatmap(corr_df, annot=True, cmap="coolwarm", ax=ax)
        st.pyplot(fig, use_container_width=True)

    # ===== PRICE HISTORY TAB =====
    with tab_price:
        st.subheader("Price History")

        col_left, col_right = st.columns([1, 3])
        with col_left:
            selected_symbol = st.selectbox(
                "Select symbol to visualize:",
                symbols,
            )
            st.write("Showing closing price over time.")

        with col_right:
            try:
                price_df = load_price_history(selected_symbol)
                st.line_chart(price_df["close"])
            except Exception as e:
                st.error(f"Price chart error for {selected_symbol}: {e}")


if __name__ == "__main__":
    main()

# src/analytics.py

import sqlite3
from typing import List, Dict

import numpy as np
import pandas as pd

from config import DB_PATH


def load_price_series(symbol: str) -> pd.DataFrame:
    """Load close prices for a symbol from the SQLite database."""
    conn = sqlite3.connect(DB_PATH)

    query = """
        SELECT date, close
        FROM prices
        WHERE symbol = ?
        ORDER BY date;
    """

    df = pd.read_sql_query(query, conn, params=(symbol,), parse_dates=["date"])
    conn.close()

    if df.empty:
        raise ValueError(f"No data found for symbol: {symbol}")

    df.set_index("date", inplace=True)
    df["return"] = df["close"].pct_change()
    df.dropna(inplace=True)
    return df


def calculate_metrics_for_symbol(symbol: str) -> Dict[str, float]:
    """Return basic risk & performance metrics for one symbol."""
    df = load_price_series(symbol)

    daily_ret = df["return"].mean()
    daily_vol = df["return"].std()

    # Annualize assuming 252 trading days
    annual_ret = daily_ret * 252
    annual_vol = daily_vol * np.sqrt(252)

    # Sharpe with rf ~ 0 for simplicity
    sharpe = annual_ret / annual_vol if annual_vol != 0 else 0.0

    # 95% historical Value-at-Risk (left tail)
    var_95 = np.percentile(df["return"], 5)

    metrics = {
        "symbol": symbol,
        "days": int(len(df)),
        "annual_return": round(annual_ret, 4),
        "annual_volatility": round(annual_vol, 4),
        "sharpe_ratio": round(sharpe, 2),
        "VaR_95_daily": round(var_95, 4)
    }
    return metrics


def calculate_portfolio_metrics(symbols: List[str],
                                weights: List[float] = None) -> Dict[str, float]:
    """Equal-weight or custom-weight portfolio metrics based on daily returns."""
    if weights is None:
        weights = [1.0 / len(symbols)] * len(symbols)

    if len(symbols) != len(weights):
        raise ValueError("Symbols and weights must have same length.")

    # Load all series and align on date
    series_list = []
    for sym in symbols:
        df = load_price_series(sym)
        series_list.append(df["return"].rename(sym))

    returns_df = pd.concat(series_list, axis=1).dropna()

    w = np.array(weights)
    daily_portfolio_returns = returns_df.dot(w)

    daily_ret = daily_portfolio_returns.mean()
    daily_vol = daily_portfolio_returns.std()

    annual_ret = daily_ret * 252
    annual_vol = daily_vol * np.sqrt(252)
    sharpe = annual_ret / annual_vol if annual_vol != 0 else 0.0
    var_95 = np.percentile(daily_portfolio_returns, 5)

    metrics = {
        "symbols": symbols,
        "weights": [round(float(x), 3) for x in w],
        "days": int(len(daily_portfolio_returns)),
        "annual_return": round(annual_ret, 4),
        "annual_volatility": round(annual_vol, 4),
        "sharpe_ratio": round(sharpe, 2),
        "VaR_95_daily": round(var_95, 4)
    }
    return metrics


if __name__ == "__main__":
    # Quick test
    symbols = ["AAPL", "MSFT", "GOOGL"]
    for s in symbols:
        print(calculate_metrics_for_symbol(s))

    print("\nPortfolio metrics:")
    print(calculate_portfolio_metrics(symbols))

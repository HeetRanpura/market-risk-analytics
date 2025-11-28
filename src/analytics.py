# src/analytics.py

import sqlite3
from typing import List, Dict

import numpy as np
import pandas as pd

from config import DB_PATH


def load_price_series(symbol: str) -> pd.DataFrame:
    """Load close prices & daily returns for a symbol from the SQLite DB."""
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
    df = load_price_series(symbol)
    daily_ret = df["return"].mean()
    daily_vol = df["return"].std()

    annual_ret = daily_ret * 252
    annual_vol = daily_vol * np.sqrt(252)
    sharpe = annual_ret / annual_vol if annual_vol != 0 else 0.0
    var95 = np.percentile(df["return"], 5)

    return {
        "symbol": symbol,
        "annual_return": round(annual_ret, 4),
        "annual_volatility": round(annual_vol, 4),
        "sharpe_ratio": round(sharpe, 2),
        "VaR_95_daily": round(var95, 4),
    }


def calculate_portfolio_metrics(symbols: List[str],
                                weights: List[float] = None) -> Dict[str, float]:
    if weights is None:
        weights = [1.0 / len(symbols)] * len(symbols)

    series_list = [load_price_series(sym)["return"].rename(sym) for sym in symbols]
    returns_df = pd.concat(series_list, axis=1).dropna()

    w = np.array(weights)
    daily_ret = returns_df.dot(w).mean()
    daily_vol = returns_df.dot(w).std()

    annual_ret = daily_ret * 252
    annual_vol = daily_vol * np.sqrt(252)
    sharpe = annual_ret / annual_vol if annual_vol != 0 else 0.0
    var95 = np.percentile(returns_df.dot(w), 5)

    return {
        "symbols": symbols,
        "weights": [round(float(x), 3) for x in w],
        "annual_return": round(annual_ret, 4),
        "annual_volatility": round(annual_vol, 4),
        "sharpe_ratio": round(sharpe, 2),
        "VaR_95_daily": round(var95, 4),
    }


# ---------------- NEW FEATURES BELOW ---------------- #

def calculate_max_drawdown(symbol: str) -> float:
    df = load_price_series(symbol)
    df["cumulative"] = (1 + df["return"]).cumprod()
    peak = df["cumulative"].cummax()
    drawdown = (df["cumulative"] - peak) / peak
    return round(float(drawdown.min()), 4)


def calculate_correlations(symbols: List[str]) -> pd.DataFrame:
    series = [load_price_series(sym)["return"].rename(sym) for sym in symbols]
    corr_df = pd.concat(series, axis=1).dropna()
    return corr_df.corr()

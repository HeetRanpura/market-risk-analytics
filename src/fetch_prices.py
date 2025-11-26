# src/fetch_prices.py

import sqlite3
from datetime import datetime
from typing import List

import yfinance as yf

from config import DB_PATH, DEFAULT_SYMBOLS, DEFAULT_PERIOD, DEFAULT_INTERVAL


def fetch_prices_for_symbol(symbol: str, period: str, interval: str):
    print(f"Fetching data for {symbol} ({period}, {interval})...")
    data = yf.download(symbol, period=period, interval=interval, progress=False)

    if data.empty:
        print(f"No data returned for {symbol}.")
        return []

    rows = []
    for index, row in data.iterrows():
        date_str = index.strftime("%Y-%m-%d")
        rows.append((
            symbol,
            date_str,
            float(row["Open"]),
            float(row["High"]),
            float(row["Low"]),
            float(row["Close"]),
            int(row["Volume"])
        ))
    return rows


def store_prices(rows):
    if not rows:
        return

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.executemany("""
        INSERT INTO prices(symbol, date, open, high, low, close, volume)
        VALUES (?, ?, ?, ?, ?, ?, ?);
    """, rows)

    conn.commit()
    conn.close()
    print(f"Inserted {len(rows)} rows.")


def fetch_and_store(symbols: List[str] = None,
                    period: str = None,
                    interval: str = None):
    if symbols is None:
        symbols = DEFAULT_SYMBOLS
    if period is None:
        period = DEFAULT_PERIOD
    if interval is None:
        interval = DEFAULT_INTERVAL

    print("Starting price download...")
    for sym in symbols:
        rows = fetch_prices_for_symbol(sym, period, interval)
        store_prices(rows)
    print("Done fetching all symbols.")


if __name__ == "__main__":
    fetch_and_store()

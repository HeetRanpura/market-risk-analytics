# src/run_example.py

from config import DEFAULT_SYMBOLS
from analytics import calculate_metrics_for_symbol, calculate_portfolio_metrics


def main():
    print("=== Individual Symbol Metrics ===")
    for sym in DEFAULT_SYMBOLS:
        try:
            m = calculate_metrics_for_symbol(sym)
            print(m)
        except Exception as e:
            print(f"Error for {sym}: {e}")

    print("\n=== Equal-Weight Portfolio Metrics ===")
    try:
        p = calculate_portfolio_metrics(DEFAULT_SYMBOLS)
        print(p)
    except Exception as e:
        print(f"Portfolio error: {e}")


if __name__ == "__main__":
    main()

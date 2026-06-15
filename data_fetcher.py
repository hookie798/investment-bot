"""
Data fetcher module — stable version for Level 4 bot
"""

from datetime import datetime, timedelta
from typing import Optional

import pandas as pd
import yfinance as yf


NASDAQ_TICKER = "QQQ"
LOOKBACK_DAYS = 365 * 3
RISK_FREE_TICKER = "BND"


def _clean_index(df: pd.DataFrame) -> pd.DataFrame:
    """Normalize datetime index to avoid timezone bugs."""
    df = df.copy()

    try:
        # 去时区（关键修复）
        if df.index.tz is not None:
            df.index = df.index.tz_convert(None)
    except Exception:
        pass

    return df


def fetch_nasdaq_data() -> Optional[dict]:
    try:
        qqq = yf.Ticker(NASDAQ_TICKER)

        end = datetime.now()
        start = end - timedelta(days=LOOKBACK_DAYS)

        hist = qqq.history(
            start=start.strftime("%Y-%m-%d"),
            end=end.strftime("%Y-%m-%d")
        )

        if hist is None or hist.empty:
            print("[ERROR] NASDAQ history empty")
            return None

        hist = _clean_index(hist)

        close_prices = hist["Close"].dropna()

        if len(close_prices) < 2:
            print("[ERROR] Not enough price data")
            return None

        current_price = float(close_prices.iloc[-1])
        previous_close = float(close_prices.iloc[-2])

        change_pct = round((current_price - previous_close) / previous_close * 100, 2)

        ath_price = float(close_prices.max())
        ath_idx = close_prices.idxmax()

        ath_date = (
            ath_idx.strftime("%Y-%m-%d")
            if hasattr(ath_idx, "strftime")
            else str(ath_idx)[:10]
        )

        drawdown_pct = round((current_price - ath_price) / ath_price * 100, 2)

        # YTD
        ytd_start = datetime(end.year, 1, 1)
        ytd_data = close_prices[close_prices.index >= ytd_start]

        if len(ytd_data) > 0:
            ytd_return = round(
                (current_price - float(ytd_data.iloc[0])) / float(ytd_data.iloc[0]) * 100,
                2
            )
        else:
            ytd_return = 0.0

        return {
            "ticker": NASDAQ_TICKER,
            "current_price": current_price,
            "previous_close": previous_close,
            "change_pct": change_pct,
            "drawdown_pct": drawdown_pct,
            "ath_price": ath_price,
            "ath_date": ath_date,
            "ytd_return_pct": ytd_return,
            "fetch_time": end.strftime("%Y-%m-%d %H:%M:%S"),
        }

    except Exception as exc:
        print(f"[ERROR] NASDAQ fetch failed: {exc}")
        return None


def fetch_bond_data() -> Optional[dict]:
    try:
        bnd = yf.Ticker(RISK_FREE_TICKER)

        end = datetime.now()
        start = end - timedelta(days=90)

        hist = bnd.history(
            start=start.strftime("%Y-%m-%d"),
            end=end.strftime("%Y-%m-%d")
        )

        if hist is None or hist.empty:
            return {"ticker": RISK_FREE_TICKER, "current_price": 0.0}

        hist = _clean_index(hist)

        current = float(hist["Close"].dropna().iloc[-1])

        return {
            "ticker": RISK_FREE_TICKER,
            "current_price": current
        }

    except Exception as exc:
        print(f"[WARN] Bond fetch failed: {exc}")
        return {"ticker": RISK_FREE_TICKER, "current_price": 0.0}


if __name__ == "__main__":
    data = fetch_nasdaq_data()
    print(data)
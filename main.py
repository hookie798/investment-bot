#!/usr/bin/env python3
"""
investment-bot — Level 4 Automated Investment Decision System
Stable Version (Fixed)

- Fix: None handling
- Fix: missing fields safety
- Fix: emoji encoding
- Fix: safer data access
"""

import json
import os
import sys
from datetime import datetime

from data_fetcher import fetch_nasdaq_data, fetch_bond_data
from strategy import DCA_AMOUNT_RMB, evaluate
from wechat import send_wechat_message


STATE_FILE = os.path.join(
    os.path.dirname(os.path.abspath(__file__)),
    "portfolio_state.json"
)

DEFAULT_STATE = {
    "nasdaq_value_rmb": 50000.0,
    "bond_value_rmb": 30000.0,
    "last_updated": "",
}


def load_portfolio():
    if os.path.exists(STATE_FILE):
        try:
            with open(STATE_FILE, "r", encoding="utf-8") as f:
                state = json.load(f)
            for k, v in DEFAULT_STATE.items():
                state.setdefault(k, v)
            return state
        except Exception:
            print("[WARN] State file corrupted, using default.")
    return dict(DEFAULT_STATE)


def save_portfolio(state):
    state["last_updated"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    with open(STATE_FILE, "w", encoding="utf-8") as f:
        json.dump(state, f, indent=2, ensure_ascii=False)


def run(dry_run: bool = False):
    print("=" * 55)
    print("📊 investment-bot — Daily Investment Signal")
    print("=" * 55)

    # ── 1. market data ─────────────────────────
    print("\n[1/4] Fetching NASDAQ market data ...")
    nasdaq = fetch_nasdaq_data()

    if not nasdaq:
        msg = "❌ Failed to fetch NASDAQ data. Aborting."
        print(msg)
        if not dry_run:
            send_wechat_message(msg)
        return 1

    print(
        f"      Price: {nasdaq.get('current_price', 0):,.2f} | "
        f"DD: {nasdaq.get('drawdown_pct', 0)}% | "
        f"YTD: {nasdaq.get('ytd_return_pct', 0)}%"
    )

    bond = fetch_bond_data() or {"current_price": 0}

    # ── 2. portfolio ─────────────────────────
    print("\n[2/4] Loading portfolio state ...")
    portfolio = load_portfolio()

    nasdaq_val = portfolio["nasdaq_value_rmb"]
    bond_val = portfolio["bond_value_rmb"]

    print(f"      NASDAQ: ¥{nasdaq_val:,.0f} | Bonds: ¥{bond_val:,.0f}")

    # ── 3. strategy ─────────────────────────
    print("\n[3/4] Evaluating investment decision ...")

    decision = evaluate(
        nasdaq_price=nasdaq.get("current_price", 0),
        nasdaq_drawdown_pct=nasdaq.get("drawdown_pct", 0),
        nasdaq_current_value=nasdaq_val,
        bond_current_value=bond_val,
        ytd_return_pct=nasdaq.get("ytd_return_pct", 0),
        extra={
            "ath_price": nasdaq.get("ath_price", 0),
            "ath_date": nasdaq.get("ath_date", ""),
            "bond_price": bond.get("current_price", 0),
        },
    )

    print(f"      Action: {decision.action} | DCA: ¥{DCA_AMOUNT_RMB}")

    # ── 4. update portfolio ─────────────────────────
    if not dry_run:
        portfolio["nasdaq_value_rmb"] = round(
            nasdaq_val + DCA_AMOUNT_RMB, 2
        )
        save_portfolio(portfolio)

        print(f"      Updated NASDAQ: ¥{portfolio['nasdaq_value_rmb']:,.0f}")

    # ── 5. push ─────────────────────────
    print("\n[4/4] Sending signal ...")

    if not dry_run:
        send_wechat_message(decision.message)
    else:
        print(decision.message)

    print("\n✅ Done.\n")
    return 0


if __name__ == "__main__":
    dry = "--dry-run" in sys.argv
    sys.exit(run(dry))
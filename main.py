#!/usr/bin/env python3
"""
investment-bot — Level 4 Automated Investment System (PushPlus Version)

Features:
- Fetch NASDAQ proxy (QQQ)
- Strategy evaluation
- Portfolio state tracking
- PushPlus WeChat notification
"""

import json
import os
import sys
from datetime import datetime

from data_fetcher import fetch_nasdaq_data, fetch_bond_data
from strategy import DCA_AMOUNT_RMB, evaluate
from wechat import send_wechat_message


# ── Portfolio state file ─────────────────────────────────────────────
STATE_FILE = os.path.join(
    os.path.dirname(os.path.abspath(__file__)),
    "portfolio_state.json"
)

DEFAULT_STATE = {
    "nasdaq_value_rmb": 50000.0,
    "bond_value_rmb": 30000.0,
    "last_updated": ""
}


# ── Load state ───────────────────────────────────────────────────────
def load_portfolio():
    if os.path.exists(STATE_FILE):
        try:
            with open(STATE_FILE, "r", encoding="utf-8") as f:
                state = json.load(f)
            for k, v in DEFAULT_STATE.items():
                state.setdefault(k, v)
            return state
        except Exception:
            print("[WARN] corrupted state file, reset to default")
    return DEFAULT_STATE.copy()


# ── Save state ───────────────────────────────────────────────────────
def save_portfolio(state):
    state["last_updated"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    with open(STATE_FILE, "w", encoding="utf-8") as f:
        json.dump(state, f, indent=2, ensure_ascii=False)


# ── Main run ─────────────────────────────────────────────────────────
def run(dry_run=False):
    print("=" * 60)
    print("📊 investment-bot — Daily Investment Signal")
    print("=" * 60)

    # 1️⃣ Fetch market data
    print("\n[1/4] Fetching NASDAQ data ...")
    nasdaq = fetch_nasdaq_data()

    if not nasdaq:
        msg = "❌ Failed to fetch NASDAQ data"
        print(msg)
        if not dry_run:
            TOKEN = os.getenv("PUSHPLUS_TOKEN")
            send_wechat_message(msg, TOKEN)
        return 1

    print(f"      Price: {nasdaq['current_price']} | DD: {nasdaq['drawdown_pct']}% | YTD: {nasdaq['ytd_return_pct']}%")

    bond = fetch_bond_data()

    # 2️⃣ Load portfolio
    print("\n[2/4] Loading portfolio state ...")
    portfolio = load_portfolio()

    nasdaq_val = portfolio["nasdaq_value_rmb"]
    bond_val = portfolio["bond_value_rmb"]

    print(f"      NASDAQ: ¥{nasdaq_val:,.0f} | Bonds: ¥{bond_val:,.0f}")

    # 3️⃣ Strategy
    print("\n[3/4] Evaluating strategy ...")

    decision = evaluate(
        nasdaq_price=nasdaq["current_price"],
        nasdaq_drawdown_pct=nasdaq["drawdown_pct"],
        nasdaq_current_value=nasdaq_val,
        bond_current_value=bond_val,
        ytd_return_pct=nasdaq.get("ytd_return_pct"),
        extra={
            "ath_price": nasdaq["ath_price"],
            "ath_date": nasdaq["ath_date"],
            "bond_price": bond["current_price"] if bond else None,
        }
    )

    print(f"      Action: {decision.action} | DCA: ¥{decision.dca_amount_rmb}")

    # 4️⃣ Update portfolio
    if not dry_run:
        portfolio["nasdaq_value_rmb"] += DCA_AMOUNT_RMB
        save_portfolio(portfolio)
        print(f"      Updated NASDAQ: ¥{portfolio['nasdaq_value_rmb']:,.0f}")

    # 5️⃣ Push notification
    print("\n[4/4] Sending signal ...")

    TOKEN = os.getenv("PUSHPLUS_TOKEN")

    if not dry_run:
        send_wechat_message(decision.message, TOKEN)
    else:
        print(decision.message)

    print("\n✅ Done.")
    return 0


# ── Entry ────────────────────────────────────────────────────────────
if __name__ == "__main__":
    dry = "--dry-run" in sys.argv
    exit(run(dry))

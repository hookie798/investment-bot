#!/usr/bin/env python3
"""
investment-bot — Level 4 Automated Investment System (PushPlus version)

Features:
- Fetch QQQ (NASDAQ proxy)
- Fetch BND (bond proxy)
- Evaluate allocation strategy
- Persist portfolio state
- Push signals via PushPlus (GitHub Actions friendly)
"""

import json
import os
import sys
from datetime import datetime

from data_fetcher import fetch_nasdaq_data, fetch_bond_data
from strategy import DCA_AMOUNT_RMB, evaluate
from wechat import send_wechat_message


# ── State file ─────────────────────────────────────────────
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
STATE_FILE = os.path.join(BASE_DIR, "portfolio_state.json")


DEFAULT_STATE = {
    "nasdaq_value_rmb": 50000.0,
    "bond_value_rmb": 30000.0,
    "last_updated": ""
}


def load_state():
    if os.path.exists(STATE_FILE):
        try:
            with open(STATE_FILE, "r", encoding="utf-8") as f:
                data = json.load(f)
            for k, v in DEFAULT_STATE.items():
                data.setdefault(k, v)
            return data
        except Exception:
            print("[WARN] state file corrupted, using default")
    return DEFAULT_STATE.copy()


def save_state(state):
    state["last_updated"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    with open(STATE_FILE, "w", encoding="utf-8") as f:
        json.dump(state, f, indent=2, ensure_ascii=False)


# ── main logic ─────────────────────────────────────────────
def run(dry_run=False):
    print("=" * 60)
    print("📊 investment-bot — Daily Signal Engine")
    print("=" * 60)

    # 1. market data
    print("\n[1/4] Fetching market data...")

    try:
        nasdaq = fetch_nasdaq_data()
    except Exception as e:
        nasdaq = None
        print("[ERROR] fetch_nasdaq failed:", e)

    if not nasdaq:
        msg = "❌ Failed to fetch NASDAQ data"
        print(msg)
        send_wechat_message(msg)
        return 1

    print(f"      Price: {nasdaq['current_price']} | DD: {nasdaq['drawdown_pct']}% | YTD: {nasdaq['ytd_return_pct']}%")

    bond = fetch_bond_data()

    # 2. portfolio state
    print("\n[2/4] Loading portfolio...")
    state = load_state()

    nasdaq_val = state["nasdaq_value_rmb"]
    bond_val = state["bond_value_rmb"]

    print(f"      NASDAQ: ¥{nasdaq_val:,.0f} | Bonds: ¥{bond_val:,.0f}")

    # 3. strategy
    print("\n[3/4] Evaluating strategy...")

    decision = evaluate(
        nasdaq_price=nasdaq["current_price"],
        nasdaq_drawdown_pct=nasdaq["drawdown_pct"],
        nasdaq_current_value=nasdaq_val,
        bond_current_value=bond_val,
        ytd_return_pct=nasdaq.get("ytd_return_pct"),
        extra={
            "ath_price": nasdaq["ath_price"],
            "ath_date": nasdaq["ath_date"],
            "bond_price": bond["current_price"] if bond else None
        }
    )

    print(f"      Action: {decision.action} | DCA: ¥{decision.dca_amount_rmb}")

    # 4. update portfolio
    if not dry_run:
        state["nasdaq_value_rmb"] = round(nasdaq_val + DCA_AMOUNT_RMB, 2)
        save_state(state)
        print(f"      Updated NASDAQ: ¥{state['nasdaq_value_rmb']:,.0f}")

    # 5. push notification
    print("\n[4/4] Sending signal...")

    try:
        send_wechat_message(decision.message)
    except Exception as e:
        print("[ERROR] push failed:", e)

    print("\n✅ Done\n")
    return 0


# ── CLI ─────────────────────────────────────────────
if __name__ == "__main__":
    dry = "--dry-run" in sys.argv
    raise SystemExit(run(dry))

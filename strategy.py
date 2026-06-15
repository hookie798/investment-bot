"""
Strategy module — portfolio allocation and daily investment decision engine.

Level 4 Stable Version
"""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional


# ── Constants ─────────────────────────────────────────────
DCA_AMOUNT_RMB = 100
ALLOCATION_THRESHOLD = 0.70
DRAWDOWN_THRESHOLD = -0.20


@dataclass
class Decision:
    date: str
    dca_amount_rmb: float = DCA_AMOUNT_RMB
    action: str = "DCA_BUY"
    nasdaq_price: float = 0.0
    nasdaq_drawdown_pct: float = 0.0
    nasdaq_allocation_pct: float = 0.0
    message: str = ""
    extra_details: dict = field(default_factory=dict)


def evaluate(
    *,
    nasdaq_price: float,
    nasdaq_drawdown_pct: float,
    nasdaq_current_value: float,
    bond_current_value: float,
    ytd_return_pct: Optional[float] = None,
    extra: Optional[dict] = None,
) -> Decision:

    total = nasdaq_current_value + bond_current_value
    allocation = (nasdaq_current_value / total) if total > 0 else 0.0
    allocation_pct = round(allocation * 100, 1)

    signals = []

    # ── Rule 1: DCA always on ──
    dca_amount = DCA_AMOUNT_RMB

    # ── Rule 2: Drawdown rule (FIXED) ──
    if nasdaq_drawdown_pct <= (DRAWDOWN_THRESHOLD * 100):
        action = "DCA_ONLY"
        signals.append("Drawdown exceeds -20%, DCA only mode activated.")
    
    # ── Rule 3: Allocation risk ──
    elif allocation > ALLOCATION_THRESHOLD:
        action = "REBALANCE_WARN"
        signals.append("NASDAQ allocation too high, consider increasing bonds.")
    
    else:
        action = "DCA_BUY"
        signals.append("Normal market condition, continue DCA.")

    # ── Message build (stable format, no emoji risk) ──
    message = (
        f"Daily Investment Signal | {datetime.now().strftime('%Y-%m-%d')}\n"
        f"----------------------------------------\n"
        f"NASDAQ Price: {nasdaq_price:.2f}\n"
        f"Drawdown: {nasdaq_drawdown_pct}%\n"
        f"Allocation: {allocation_pct}%\n"
        f"YTD Return: {ytd_return_pct if ytd_return_pct is not None else 'N/A'}%\n"
        f"----------------------------------------\n"
        f"Action: {action}\n"
        f"DCA: {dca_amount} RMB\n"
        f"Note: {signals[0] if signals else ''}\n"
        f"----------------------------------------\n"
    )

    return Decision(
        date=datetime.now().strftime("%Y-%m-%d"),
        dca_amount_rmb=dca_amount,
        action=action,
        nasdaq_price=nasdaq_price,
        nasdaq_drawdown_pct=nasdaq_drawdown_pct,
        nasdaq_allocation_pct=allocation_pct,
        message=message,
        extra_details=extra or {},
    )


# ── test ──
if __name__ == "__main__":
    d = evaluate(
        nasdaq_price=420,
        nasdaq_drawdown_pct=-15,
        nasdaq_current_value=50000,
        bond_current_value=30000,
        ytd_return_pct=8.5,
    )
    print(d.message)
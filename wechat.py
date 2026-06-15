"""
WeChat push module — stable Level 4 version.

- Default: mock push (console + log file)
- Optional: real webhook (WeCom / ServerChan / PushPlus)
"""

import os
from datetime import datetime

LOG_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "logs")
LOG_FILE = os.path.join(LOG_DIR, "investment_signals.log")


def _ensure_log_dir():
    """Ensure logs directory exists safely."""
    os.makedirs(LOG_DIR, exist_ok=True)


def _write_log(timestamp: str, message: str):
    """Append message to local log file."""
    with open(LOG_FILE, "a", encoding="utf-8") as f:
        f.write("\n" + "=" * 60 + "\n")
        f.write(f"[{timestamp}]\n")
        f.write(message + "\n")
        f.write("=" * 60 + "\n")


def send_wechat_message(message: str, webhook_url: str = "") -> bool:
    """
    Send investment signal (mock or real webhook).
    """

    _ensure_log_dir()

    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    # ─────────────────────────────
    # MOCK MODE (default)
    # ─────────────────────────────
    if not webhook_url:

        print("\n" + "─" * 50)
        print(f"[WeChat Mock Push] {timestamp}")
        print("─" * 50)
        print(message)
        print("─" * 50 + "\n")

        _write_log(timestamp, message)
        return True

    # ─────────────────────────────
    # REAL WEBHOOK MODE (optional)
    # ─────────────────────────────
    try:
        import requests

        payload = {
            "msgtype": "markdown",
            "markdown": {
                "content": message
            }
        }

        resp = requests.post(webhook_url, json=payload, timeout=10)

        success = (
            resp.status_code == 200
            and resp.json().get("errcode", 1) == 0
        )

        if not success:
            print(f"[WARN] Webhook failed: {resp.text}")

        return success

    except Exception as exc:
        print(f"[ERROR] WeChat push exception: {exc}")
        return False


# ── test ─────────────────────────────────────────────
if __name__ == "__main__":
    send_wechat_message("Test: DCA_BUY signal — system OK.")
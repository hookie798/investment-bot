"""
PushPlus notification module (production ready)

Usage:
    - Set environment variable:
        PUSHPLUS_TOKEN=xxxxxx
"""

import os
import requests
from datetime import datetime

LOG_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "logs")
LOG_FILE = os.path.join(LOG_DIR, "investment_signals.log")


def _ensure_log_dir():
    os.makedirs(LOG_DIR, exist_ok=True)


def send_wechat_message(message: str, token: str = None) -> bool:
    """
    Push message via PushPlus.
    """

    _ensure_log_dir()
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    token = token or os.getenv("PUSHPLUS_TOKEN")

    # fallback: local log if no token
    if not token:
        print("[WARN] No PUSHPLUS_TOKEN found, fallback to local log only")
        print(message)
        return False

    url = "http://www.pushplus.plus/send"

    payload = {
        "token": token,
        "title": "investment-bot daily signal",
        "content": message,
        "template": "txt"
    }

    try:
        resp = requests.post(url, json=payload, timeout=10)
        result = resp.json()

        ok = result.get("code") == 200

        print("─" * 50)
        print(f"[PushPlus] {timestamp}")
        print("─" * 50)
        print(result)
        print("─" * 50)

        # log locally
        with open(LOG_FILE, "a", encoding="utf-8") as f:
            f.write(f"\n[{timestamp}]\n{message}\n")

        return ok

    except Exception as e:
        print(f"[ERROR] PushPlus failed: {e}")
        return False

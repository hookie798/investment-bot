import requests
from datetime import datetime

def send_wechat_message(message: str, token: str):
    """
    PushPlus 微信推送
    """

    url = "http://www.pushplus.plus/send"

    payload = {
        "token": token,
        "title": "investment-bot 日报",
        "content": message,
        "template": "markdown"
    }

    try:
        resp = requests.post(url, json=payload, timeout=10)
        data = resp.json()

        if data.get("code") == 200:
            print("[PushPlus] sent successfully")
            return True
        else:
            print("[PushPlus Error]", data)
            return False

    except Exception as e:
        print("[PushPlus Exception]", e)
        return False

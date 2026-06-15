# 📊 investment-bot

**Level 4 Automated Investment Decision System**

A fully automated NASDAQ DCA + bond allocation decision engine powered by `yfinance`, running on GitHub Actions.

---

## 🧠 Investment Logic

| Rule | Condition | Action |
|------|-----------|--------|
| DCA baseline | Always | Invest 100 RMB/day into NASDAQ |
| Risk control | Drawdown > 20% | Continue DCA only (no extra risk) |
| Rebalance | NASDAQ allocation > 70% | Recommend increasing bonds |

---

## 📁 Project Structure


```
investment-bot/
├── main.py
├── data_fetcher.py
├── strategy.py
├── wechat.py
├── requirements.txt
├── portfolio_state.json
├── logs/
├── .github/workflows/daily.yml
└── README.md
```


---

## 🚀 Quick Start

```bash
git clone https://github.com/<your-username>/investment-bot.git
cd investment-bot

pip install -r requirements.txt

# dry run (no state change)
python main.py --dry-run

# real run
python main.py
The GitHub Actions workflow (`daily.yml`) triggers:

- **Scheduled**: 9:00 AM Beijing time, Monday–Friday (`0 1 * * 1-5` UTC)
- **Manual**: `workflow_dispatch` button on the Actions tab
- **Push**: on every push to `main` that touches Python files

Each run:
1. Fetches QQQ & BND prices
2. Evaluates the decision rules
3. Logs the signal & pushes updated `portfolio_state.json` back to the repo

### Enabling the schedule

1. Push the repo to GitHub
2. Go to **Settings → Actions → General → Workflow permissions**
3. Set to **Read and write permissions**
4. The schedule activates automatically

---

## ?? Switching to Real WeChat Push

In `wechat.py`, uncomment the `requests.post(...)` block and
set your webhook URL via environment variable:

```bash
export WECHAT_WEBHOOK_URL="https://qyapi.weixin.qq.com/cgi-bin/webhook/send?key=YOUR_KEY"
```

Then modify `main.py` to pass `os.environ["WECHAT_WEBHOOK_URL"]` to
`send_wechat_message()`.

Alternative push channels (easy to swap in):
- [ServerChan ??](https://sct.ftqq.com/)
- [PushPlus](https://www.pushplus.plus/)
- Telegram Bot / Slack webhook

---

## ?? License

MIT — use it, fork it, deploy it. Trade at your own risk; this is not financial advice.

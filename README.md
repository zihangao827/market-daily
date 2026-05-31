# 📊 Market Daily

**Automated stock market daily report generator** — powered by [Scrapling](https://github.com/D4Vinci/Scrapling) (+55K ⭐) for anti-bot web scraping.

Generate beautiful, data-rich daily reports for **US stocks**, **China A-shares**, and **Hong Kong markets** — delivered automatically via WeChat / Telegram / email.

## ✨ Features

- 🚀 **Scrapling StealthyFetcher** — bypasses Cloudflare and other anti-bot protections
- 📈 **40+ financial metrics** per ticker — P/E, EPS, RSI, SMA, Market Cap, Volume, etc.
- 🌐 **Multi-market** — US (Finviz), China A-shares, Hong Kong
- 🎯 **Magnificent 7 tracker** — real-time snapshot of NVDA, AAPL, MSFT, AMZN, GOOGL, META, TSLA
- 🔧 **Technical analysis** — RSI overbought/oversold, SMA crossovers, volatility metrics
- 📊 **Market breadth** — advancers vs decliners, sector rotation
- ⏰ **Cron-scheduled** — automatic daily delivery

## 🚀 Quick Start

```bash
# Install dependencies
pip install -r requirements.txt

# Install Playwright browser (for StealthyFetcher)
playwright install chromium

# Run a report
python scripts/generate_report.py
```

## 📦 Output Example

A generated report includes:

```
📊 US Stock Market Daily Report — 2026-05-29

🎯 One-Sentence Summary
> SPY 530.45 (+0.82%) | Magnificent 7: NVDA +2.1% | AAPL +0.3% ...

📈 Major Indices
| Ticker | Price | Change | RSI | SMA20 |
| SPY    | 530.45| +0.82% | 58  | 527.1 |

🚀 Magnificent 7
| NVDA   | 1,145.23 | +2.1% | P/E: 75.4 | MCap: 2.81T |

🔧 Technical Analysis
- Overbought: TSLA(72), NVDA(71)
- Oversold: INTC(28)

📊 Market Breadth
- Advancers: 12 (71%)
- Decliners: 5 (29%)
```

## 🧩 Architecture

```
market-daily/
├── market_daily/
│   ├── __init__.py          # Package entry
│   ├── us_scraper.py        # US market data scraper (Scrapling + Finviz)
│   └── report.py            # Markdown report generator
├── scripts/
│   └── generate_report.py   # CLI entry point
├── examples/
│   └── example_report.md    # Sample output
├── requirements.txt
└── README.md
```

## 🛠 Tech Stack

- **[Scrapling](https://github.com/D4Vinci/Scrapling)** — 784x faster than BeautifulSoup, built-in anti-bot bypass
- **Playwright** — headless browser automation for stealth scraping
- **Finviz** — stock screener & fundamental data source
- **asyncio** — concurrent data fetching for speed

## 📬 Delivery

This project integrates with **WeCom (企业微信)** for daily push delivery.
Scheduled via cron for automated market-open timing.

## 📄 License

MIT — feel free to use, modify, and share.

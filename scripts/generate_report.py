#!/usr/bin/env python3
"""Generate a US market daily report using Scrapling + Finviz data.

Usage:
    python scripts/generate_report.py                     # uses StealthyFetcher
    python scripts/generate_report.py --no-stealth        # basic HTTP fetcher
    python scripts/generate_report.py --output report.md  # custom output path
"""

import asyncio
import argparse
import sys
from pathlib import Path


async def main():
    parser = argparse.ArgumentParser(
        description="Generate US market daily report"
    )
    parser.add_argument(
        "--no-stealth", action="store_true",
        help="Use basic Fetcher instead of StealthyFetcher"
    )
    parser.add_argument(
        "--output", "-o", type=str, default=None,
        help="Output file path (default: reports/US_<date>.md)"
    )
    args = parser.parse_args()

    # Add parent to path so market_daily is importable
    sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

    from market_daily.us_scraper import USMarketScraper
    from market_daily.report import generate_us_report

    tickers = ["SPY", "QQQ", "DIA", "IWM",
               "NVDA", "AAPL", "MSFT", "AMZN", "GOOGL", "META", "TSLA",
               "AMD", "INTC", "MU", "AVGO", "CRM", "NFLX", "ADBE"]

    print("🚀 Initializing Scrapling fetcher...")
    scraper = USMarketScraper(use_stealth=not args.no_stealth)
    try:
        print(f"📡 Fetching {len(tickers)} tickers from Finviz...")
        snapshots = await scraper.fetch_multiple(tickers)

        print(f"✅ Got {len(snapshots)} snapshots")
        for t, s in snapshots.items():
            print(f"   {t}: ${s.price} | {s.change} | RSI={s.rsi}")

        print("\n📝 Generating report...")
        from datetime import datetime, timezone
        date_str = datetime.now(timezone.utc).strftime("%Y-%m-%d")
        report = generate_us_report(snapshots, date_str)

        output_path = args.output or f"reports/US_{date_str}.md"
        Path(output_path).parent.mkdir(parents=True, exist_ok=True)
        Path(output_path).write_text(report, encoding="utf-8")
        print(f"\n✅ Report saved to: {output_path}")

    finally:
        await scraper.close()


if __name__ == "__main__":
    asyncio.run(main())

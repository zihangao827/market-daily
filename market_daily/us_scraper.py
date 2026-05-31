"""US market data scraper using Scrapling's StealthyFetcher.

Scrapes Finviz for real-time stock snapshots including:
- Price, P/E, Market Cap, RSI, SMA20/50
- Volume, Change, Volatility, and more (40+ fields per ticker)
"""

import re
import json
from typing import Optional
from dataclasses import dataclass, field, asdict


@dataclass
class StockSnapshot:
    """Snapshot data for a single stock ticker from Finviz."""
    ticker: str = ""
    price: str = ""
    change: str = ""
    volume: str = ""
    avg_volume: str = ""
    market_cap: str = ""
    pe: str = ""
    forward_pe: str = ""
    eps_growth: str = ""
    dividend: str = ""
    roe: str = ""
    roa: str = ""
    roic: str = ""
    gross_margin: str = ""
    operating_margin: str = ""
    net_margin: str = ""
    debt_eq: str = ""
    current_ratio: str = ""
    peg: str = ""
    ps: str = ""
    pb: str = ""
    pc: str = ""
    pfcf: str = ""
    rsi: str = ""
    sma20: str = ""
    sma50: str = ""
    sma200: str = ""
    beta: str = ""
    atr: str = ""
    volatility: str = ""
    target_price: str = ""
    insider_own: str = ""
    institution_own: str = ""
    short_float: str = ""
    short_ratio: str = ""
    income: str = ""
    revenue: str = ""
    earnings_date: str = ""
    ipo_date: str = ""

    def to_dict(self) -> dict:
        return {k: v for k, v in asdict(self).items() if v}

    @classmethod
    def from_finviz_table(cls, ticker: str, cells: list[str]) -> "StockSnapshot":
        """Parse the 168-cell table from Finviz snapshot into fields."""
        vals = cells[5::2]  # value cells are at odd indices starting from 5
        snapshot = cls(ticker=ticker)
        fields = [
            "price", "change", "volume", "avg_volume", "market_cap",
            "pe", "forward_pe", "eps_growth", "dividend", "roe",
            "roa", "roic", "gross_margin", "operating_margin", "net_margin",
            "debt_eq", "current_ratio", "peg", "ps", "pb",
            "pc", "pfcf", "rsi", "sma20", "sma50",
            "sma200", "beta", "atr", "volatility", "target_price",
            "insider_own", "institution_own", "short_float", "short_ratio",
            "income", "revenue", "earnings_date", "ipo_date",
        ]
        for i, field_name in enumerate(fields):
            if i < len(vals):
                setattr(snapshot, field_name, vals[i].strip())
        return snapshot


class USMarketScraper:
    """Scrape US stock market data from Finviz using Scrapling."""

    FINVIZ_BASE = "https://finviz.com"
    MAGNIFICENT_7 = [
        "NVDA", "AAPL", "MSFT", "AMZN", "GOOGL", "META", "TSLA"
    ]
    MAJOR_INDICES = [
        "SPY", "QQQ", "DIA", "IWM"
    ]

    def __init__(self, use_stealth: bool = True):
        self.use_stealth = use_stealth
        self._fetcher = None

    async def _get_fetcher(self):
        """Initialize Scrapling fetcher lazily."""
        if self._fetcher is None:
            if self.use_stealth:
                from scrapling import StealthyFetcher
                self._fetcher = StealthyFetcher(
                    headless=True,
                    use_stealth=True,
                    block_images=True,
                )
                await self._fetcher.start()
            else:
                from scrapling import Fetcher
                self._fetcher = Fetcher()
        return self._fetcher

    async def fetch_snapshot(self, ticker: str) -> Optional[StockSnapshot]:
        """Fetch Finviz snapshot for a single ticker.

        Returns parsed StockSnapshot or None on failure.
        """
        fetcher = await self._get_fetcher()
        url = f"{self.FINVIZ_BASE}/quote.ashx?t={ticker.lower()}&ty=c&ta=1&p=d&b=1"
        try:
            page = await fetcher.get(url)
            table = page.css("table.snapshot-table2")
            if not table:
                # Fallback: try the stock quote page directly
                page = await fetcher.get(f"{self.FINVIZ_BASE}/quote.ashx?t={ticker}")
                table = page.css("table.snapshot-table2")

            if not table:
                return None

            cells = [td.text(strip=True) for td in table[0].css("td")]
            return StockSnapshot.from_finviz_table(ticker, cells)

        except Exception as e:
            print(f"Error fetching {ticker}: {e}")
            return None

    async def fetch_multiple(self, tickers: list[str]) -> dict[str, StockSnapshot]:
        """Fetch snapshots for multiple tickers concurrently."""
        import asyncio
        tasks = [self.fetch_snapshot(t) for t in tickers]
        results = await asyncio.gather(*tasks)
        return {t: r for t, r in zip(tickers, results) if r is not None}

    async def fetch_us_market_overview(self) -> dict:
        """Fetch US market overview data (indices + major sectors)."""
        tickers = self.MAGNIFICENT_7 + self.MAJOR_INDICES
        snapshots = await self.fetch_multiple(tickers)
        return {
            "magnificent_7": {
                t: s.to_dict() for t, s in snapshots.items()
                if t in self.MAGNIFICENT_7
            },
            "indices": {
                t: s.to_dict() for t, s in snapshots.items()
                if t in self.MAJOR_INDICES
            },
        }

    async def close(self):
        """Clean up fetcher resources."""
        if self._fetcher and hasattr(self._fetcher, "stop"):
            await self._fetcher.stop()

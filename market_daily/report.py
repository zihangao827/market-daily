"""Report generation module for market daily reports.

Produces structured Markdown reports covering:
1. Executive Summary
2. Market Overview (Indices)
3. Magnificent 7 Performance
4. Technical Indicators (RSI, SMA)
5. Market Breadth & Sentiment
6. Macro Context
7. Top Gainers / Losers
"""

from datetime import datetime, timezone
from typing import Optional

from .us_scraper import StockSnapshot


def generate_us_report(
    snapshots: dict[str, StockSnapshot],
    date_str: Optional[str] = None,
) -> str:
    """Generate a full US market daily report in Markdown.

    Args:
        snapshots: Dict of ticker -> StockSnapshot
        date_str: Optional date string (defaults to UTC date)

    Returns:
        Markdown report string
    """
    if date_str is None:
        date_str = datetime.now(timezone.utc).strftime("%Y-%m-%d")

    lines = []
    lines.append(f"# 📊 US Stock Market Daily Report — {date_str}")
    lines.append("")
    lines.append("---")
    lines.append("")

    # ── Section 1: Executive Summary ──
    lines.append("## 🎯 One-Sentence Summary")
    lines.append("")
    spy = snapshots.get("SPY")
    if spy and spy.price:
        spy_change = spy.change or "N/A"
        spy_vol = spy.volume or "N/A"
        lines.append(
            f"> SPY {spy.price} ({spy_change}) | "
            f"Volume: {spy_vol} | "
            f"Magnificent 7: "
            f"{_summarize_mag7(snapshots)}"
        )
    lines.append("")

    # ── Section 2: Major Indices ──
    lines.append("## 📈 Major Indices")
    lines.append("")
    lines.append("| Ticker | Price | Change | Volume | RSI | SMA20 | SMA50 |")
    lines.append("|--------|-------|--------|--------|-----|-------|-------|")
    for idx in ["SPY", "QQQ", "DIA", "IWM"]:
        s = snapshots.get(idx)
        if s and s.price:
            lines.append(
                f"| {idx} | {s.price} | {s.change or 'N/A'} | "
                f"{s.volume or 'N/A'} | {s.rsi or 'N/A'} | "
                f"{s.sma20 or 'N/A'} | {s.sma50 or 'N/A'} |"
            )
    lines.append("")

    # ── Section 3: Magnificent 7 ──
    lines.append("## 🚀 Magnificent 7")
    lines.append("")
    lines.append("| Ticker | Price | Change | P/E | Market Cap | RSI | SMA20 |")
    lines.append("|--------|-------|--------|-----|------------|-----|-------|")
    for t in ["NVDA", "AAPL", "MSFT", "AMZN", "GOOGL", "META", "TSLA"]:
        s = snapshots.get(t)
        if s and s.price:
            lines.append(
                f"| {t} | {s.price} | {s.change or 'N/A'} | "
                f"{s.pe or 'N/A'} | {s.market_cap or 'N/A'} | "
                f"{s.rsi or 'N/A'} | {s.sma20 or 'N/A'} |"
            )
    lines.append("")

    # ── Section 4: Technical Analysis ──
    lines.append("## 🔧 Technical Analysis")
    lines.append("")
    lines.append("### RSI (14) — Overbought / Oversold")
    lines.append("")
    overbought, oversold, neutral = [], [], []
    for t, s in snapshots.items():
        if s.rsi:
            try:
                rsi_val = float(s.rsi.replace("%", ""))
                if rsi_val >= 70:
                    overbought.append((t, rsi_val))
                elif rsi_val <= 30:
                    oversold.append((t, rsi_val))
                else:
                    neutral.append((t, rsi_val))
            except ValueError:
                pass
    if overbought:
        lines.append(f"- **Overbought** (RSI ≥ 70): {', '.join(f'{t}({v})' for t, v in overbought)}")
    if oversold:
        lines.append(f"- **Oversold** (RSI ≤ 30): {', '.join(f'{t}({v})' for t, v in oversold)}")
    if neutral:
        lines.append(f"- **Neutral**: {', '.join(f'{t}({v})' for t, v in neutral)}")
    lines.append("")

    # ── Section 5: Sector Performance ──
    lines.append("## 🏭 Sector Overview")
    lines.append("")
    sector_map = {
        "Technology": ["NVDA", "AAPL", "MSFT", "AMZN", "GOOGL", "META"],
        "Consumer Cyclical": ["TSLA"],
        "Financial": [],
        "Healthcare": [],
    }
    for sector, tickers in sector_map.items():
        present = [t for t in tickers if t in snapshots]
        if not present:
            continue
        changes = []
        for t in present:
            s = snapshots[t]
            if s and s.change:
                changes.append(f"{t}({s.change})")
        if changes:
            lines.append(f"- **{sector}**: {', '.join(changes)}")
    lines.append("")

    # ── Section 6: Market Breadth ──
    lines.append("## 📊 Market Breadth")
    lines.append("")
    advancers = sum(1 for s in snapshots.values() if s.change and s.change.startswith("+"))
    decliners = sum(1 for s in snapshots.values() if s.change and s.change.startswith("-"))
    total = advancers + decliners
    if total > 0:
        lines.append(f"- **Advancers**: {advancers} ({advancers/total*100:.0f}%)")
        lines.append(f"- **Decliners**: {decliners} ({decliners/total*100:.0f}%)")
    lines.append("")

    # ── Section 7: Individual Stock Analysis ──
    lines.append("## 📋 Individual Stock Details")
    lines.append("")
    for t, s in sorted(snapshots.items()):
        if not s.price:
            continue
        lines.append(f"### {t}")
        lines.append("")
        highlights = []
        if s.pe: highlights.append(f"P/E: {s.pe}")
        if s.market_cap: highlights.append(f"Market Cap: {s.market_cap}")
        if s.rsi: highlights.append(f"RSI(14): {s.rsi}")
        if s.sma20: highlights.append(f"SMA20: {s.sma20}")
        if s.sma50: highlights.append(f"SMA50: {s.sma50}")
        if s.sma200: highlights.append(f"SMA200: {s.sma200}")
        if s.volume: highlights.append(f"Volume: {s.volume}")
        if s.avg_volume: highlights.append(f"Avg Vol: {s.avg_volume}")
        if s.beta: highlights.append(f"Beta: {s.beta}")
        if s.volatility: highlights.append(f"Volatility: {s.volatility}")
        if s.short_float: highlights.append(f"Short Float: {s.short_float}")
        if s.earnings_date: highlights.append(f"Next Earnings: {s.earnings_date}")
        if highlights:
            lines.append(" | ".join(highlights))
        lines.append("")

    # ── Footer ──
    lines.append("---")
    lines.append(f"*Generated by [market-daily](https://github.com/zihangao827/market-daily) — "
                 f"data from Finviz | {date_str}*")
    lines.append("")

    return "\n".join(lines)


def _summarize_mag7(snapshots: dict[str, StockSnapshot]) -> str:
    """Summarize Magnificent 7 performance."""
    parts = []
    for t in ["NVDA", "AAPL", "MSFT", "AMZN", "GOOGL", "META", "TSLA"]:
        s = snapshots.get(t)
        if s and s.change:
            parts.append(f"{t} {s.change}")
    return " | ".join(parts) if parts else "N/A"

"""Fetch recent news mentions for a company via Google News RSS.

No API key required. Google News RSS supports a `when:1d` filter to
restrict results to the last day, which keeps this to "what's new today".
"""
import re
import urllib.parse
import feedparser
from dateutil import parser as dtparser
from datetime import datetime, timezone, timedelta

# Sites that generate templated stock-price/competitor filler for every
# ticker daily. These aren't news — they're noise, and they show up a lot
# because Google News treats any ticker mention as a match.
SOURCE_BLOCKLIST = {
    "marketbeat", "simplywall.st", "simply wall st", "insider monkey",
    "zacks", "gurufocus", "benzinga insider", "stocktwits",
    "yahoo finance canada", "yahoo finance",
}

# Templated headline patterns from those same content mills — belt and
# suspenders in case a junk article slips through from an unlisted source.
JUNK_TITLE_PATTERNS = [
    r"\bstock price\b",
    r"\bmoving average\b",
    r"\bcompetitors?\b",
    r"\bquote\s*&\s*history\b",
    r"\bhere'?s what happened\b",
    r"\b52.week\b",
    r"\binstitutional investors?\b",
    r"\bshares of\b.*\b(up|down)\b",
    r"\bis up \d",
    r"\bis down \d",
    r"\bprice target\b",
]


def _is_junk(title: str, source: str) -> bool:
    source_l = (source or "").lower()
    if any(bad in source_l for bad in SOURCE_BLOCKLIST):
        return True
    title_l = (title or "").lower()
    if any(re.search(pat, title_l) for pat in JUNK_TITLE_PATTERNS):
        return True
    return False


def fetch_news_for_account(name: str, lookback_days: int = 1):
    """Return a list of dicts: {title, link, source, published, account}."""
    query = urllib.parse.quote(f'"{name}" when:{lookback_days}d')
    url = f"https://news.google.com/rss/search?q={query}&hl=en-US&gl=US&ceid=US:en"

    feed = feedparser.parse(url)
    cutoff = datetime.now(timezone.utc) - timedelta(days=lookback_days + 1)

    results = []
    for entry in feed.entries:
        try:
            published = dtparser.parse(entry.published)
            if published.tzinfo is None:
                published = published.replace(tzinfo=timezone.utc)
        except Exception:
            published = datetime.now(timezone.utc)

        if published < cutoff:
            continue

        source = entry.get("source", {}).get("title", "Unknown source")

        # Require the company name to actually appear in the headline —
        # cuts roundup/competitor articles that only mention it in passing.
        if name.lower() not in entry.title.lower():
            continue

        if _is_junk(entry.title, source):
            continue

        results.append({
            "account": name,
            "title": entry.title,
            "link": entry.link,
            "source": source,
            "published": published.isoformat(),
            "snippet": entry.get("summary", ""),
        })

    return results

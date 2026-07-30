"""Fetch recent news mentions for a company via Google News RSS.

No API key required. Google News RSS supports a `when:1d` filter to
restrict results to the last day, which keeps this to "what's new today".
"""
import urllib.parse
import feedparser
from dateutil import parser as dtparser
from datetime import datetime, timezone, timedelta


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

        results.append({
            "account": name,
            "title": entry.title,
            "link": entry.link,
            "source": source,
            "published": published.isoformat(),
            "snippet": entry.get("summary", ""),
        })

    return results

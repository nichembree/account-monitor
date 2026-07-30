"""Combine news + EDGAR results into a single digest, deduped and grouped
by account.
"""


def build_digest(news_items, filing_items):
    """Return dict: {account_name: {"news": [...], "filings": [...]}}"""
    digest = {}

    for item in news_items:
        acct = item["account"]
        digest.setdefault(acct, {"news": [], "filings": []})
        # de-dupe on link
        if not any(n["link"] == item["link"] for n in digest[acct]["news"]):
            digest[acct]["news"].append(item)

    for item in filing_items:
        acct = item["account"]
        digest.setdefault(acct, {"news": [], "filings": []})
        if not any(f["link"] == item["link"] for f in digest[acct]["filings"]):
            digest[acct]["filings"].append(item)

    # Drop accounts with nothing to report
    digest = {k: v for k, v in digest.items() if v["news"] or v["filings"]}
    return digest

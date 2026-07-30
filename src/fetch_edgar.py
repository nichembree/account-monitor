"""Fetch recent SEC filings mentioning a company via EDGAR full-text search.

Covers 8-Ks (material events / press releases), 10-Qs, and 10-Ks.
No API key required, but SEC requires a descriptive User-Agent header
identifying who is making requests.
"""
import requests
from datetime import datetime, timedelta

EDGAR_SEARCH_URL = "https://efts.sec.gov/LATEST/search-index"

# SEC requires a real contact in the User-Agent per their fair-access policy.
# Replace the email below with yours before running for real.
HEADERS = {
    "User-Agent": "Nic Hembree Account Monitor nichembree@gmail.com"
}


def fetch_filings_for_account(name: str, lookback_days: int = 1):
    """Return a list of dicts: {title, link, form, filed, account}."""
    end = datetime.utcnow().date()
    start = end - timedelta(days=lookback_days)

    params = {
        "q": f'"{name}"',
        "forms": "8-K,10-Q,10-K",
        "startdt": start.isoformat(),
        "enddt": end.isoformat(),
    }

    try:
        resp = requests.get(EDGAR_SEARCH_URL, params=params, headers=HEADERS, timeout=15)
        resp.raise_for_status()
        data = resp.json()
    except Exception as e:
        # Fail soft: a bad/rate-limited request shouldn't kill the whole run.
        print(f"EDGAR lookup failed for {name}: {e}")
        return []

    results = []
    for hit in data.get("hits", {}).get("hits", []):
        src = hit.get("_source", {})
        cik = src.get("ciks", [None])[0]
        accession = hit.get("_id", "").split(":")[0].replace("-", "")
        filing_url = None
        if cik and accession:
            filing_url = (
                f"https://www.sec.gov/cgi-bin/browse-edgar?action=getcompany"
                f"&CIK={cik}&type={src.get('forms', '')}"
            )

        results.append({
            "account": name,
            "title": f"{src.get('forms', 'Filing')} - {src.get('display_names', [name])[0]}",
            "link": filing_url or "https://www.sec.gov/edgar/search/",
            "form": src.get("forms"),
            "filed": src.get("file_date"),
        })

    return results

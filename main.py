"""Daily account monitor — run once a day (via GitHub Actions cron).

Pulls news + SEC filings for each account in accounts.yaml, builds a
digest, writes a dashboard to docs/index.html, and emails a summary.
"""
import sys
import time
import yaml

from src.fetch_news import fetch_news_for_account
from src.fetch_edgar import fetch_filings_for_account
from src.build_digest import build_digest
from src.summarize import summarize_account
from src.generate_dashboard import generate_dashboard
from src.send_email import send_digest_email

# Set this to your published GitHub Pages URL once it's live, e.g.
# "https://yourusername.github.io/account-monitor/"
DASHBOARD_URL = None


def load_accounts(path="accounts.yaml"):
    with open(path) as f:
        data = yaml.safe_load(f)
    return data["accounts"]


def main():
    accounts = load_accounts()
    print(f"Monitoring {len(accounts)} accounts...")

    all_news = []
    all_filings = []

    for acct in accounts:
        name = acct["name"]
        print(f"  Checking {name}...")

        try:
            all_news.extend(fetch_news_for_account(name))
        except Exception as e:
            print(f"    News fetch failed for {name}: {e}")

        if acct.get("public"):
            try:
                all_filings.extend(fetch_filings_for_account(name))
            except Exception as e:
                print(f"    EDGAR fetch failed for {name}: {e}")
            # Be polite to SEC's rate limits (10 req/sec max, we go much slower)
            time.sleep(0.5)

    digest = build_digest(all_news, all_filings)
    print(f"Found activity for {len(digest)} accounts.")

    print("Summarizing...")
    for acct, entry in digest.items():
        entry["summary"] = summarize_account(acct, entry["news"], entry["filings"])

    path = generate_dashboard(digest)
    print(f"Dashboard written to {path}")

    send_digest_email(digest, dashboard_url=DASHBOARD_URL)


if __name__ == "__main__":
    sys.exit(main())

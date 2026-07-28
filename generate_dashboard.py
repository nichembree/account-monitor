"""Render the digest into a static index.html for GitHub Pages."""
from datetime import datetime

TEMPLATE = """<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<title>Account Watch — {date}</title>
<style>
  body {{ font-family: -apple-system, Segoe UI, Roboto, Arial, sans-serif;
         max-width: 760px; margin: 40px auto; padding: 0 16px; color: #1a1a1a; }}
  h1 {{ font-size: 22px; margin-bottom: 4px; }}
  .subtitle {{ color: #666; margin-bottom: 32px; }}
  .account {{ margin-bottom: 28px; border-left: 3px solid #2b6cb0; padding-left: 14px; }}
  .account h2 {{ font-size: 16px; margin: 0 0 8px 0; }}
  .item {{ margin-bottom: 8px; font-size: 14px; }}
  .item a {{ color: #2b6cb0; text-decoration: none; }}
  .item a:hover {{ text-decoration: underline; }}
  .meta {{ color: #888; font-size: 12px; }}
  .tag {{ display: inline-block; background: #edf2f7; color: #444; font-size: 11px;
          padding: 1px 6px; border-radius: 4px; margin-right: 6px; }}
  .empty {{ color: #888; font-style: italic; }}
</style>
</head>
<body>
  <h1>Account Watch</h1>
  <div class="subtitle">Daily digest — {date}</div>
  {body}
</body>
</html>
"""

ACCOUNT_TEMPLATE = """
<div class="account">
  <h2>{account}</h2>
  {items}
</div>
"""


def _render_items(digest_entry):
    rows = []
    for f in digest_entry["filings"]:
        rows.append(
            f'<div class="item"><span class="tag">SEC {f.get("form","")}</span> '
            f'<a href="{f["link"]}" target="_blank">{f["title"]}</a> '
            f'<div class="meta">Filed {f.get("filed","")}</div></div>'
        )
    for n in digest_entry["news"]:
        rows.append(
            f'<div class="item"><span class="tag">News</span> '
            f'<a href="{n["link"]}" target="_blank">{n["title"]}</a> '
            f'<div class="meta">{n.get("source","")} — {n.get("published","")[:10]}</div></div>'
        )
    return "\n".join(rows)


def generate_dashboard(digest, output_path="docs/index.html"):
    date_str = datetime.utcnow().strftime("%B %d, %Y")

    if not digest:
        body = '<p class="empty">No account activity found in the last 24 hours.</p>'
    else:
        body = "\n".join(
            ACCOUNT_TEMPLATE.format(account=acct, items=_render_items(entry))
            for acct, entry in sorted(digest.items())
        )

    html = TEMPLATE.format(date=date_str, body=body)

    with open(output_path, "w") as f:
        f.write(html)

    return output_path

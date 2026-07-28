"""Send the daily digest as an email via Gmail SMTP.

Requires a Gmail *App Password* (not your regular password) set as the
environment variable GMAIL_APP_PASSWORD. Set up at:
https://myaccount.google.com/apppasswords
(Requires 2-Step Verification to be enabled on the Google account first.)
"""
import os
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime

GMAIL_ADDRESS = "nichembree@gmail.com"


def _plaintext_summary(digest):
    if not digest:
        return "No account activity found in the last 24 hours."

    lines = []
    for acct, entry in sorted(digest.items()):
        lines.append(f"\n{acct}")
        lines.append("-" * len(acct))
        for f in entry["filings"]:
            lines.append(f"  [SEC {f.get('form','')}] {f['title']} — {f['link']}")
        for n in entry["news"]:
            lines.append(f"  [News] {n['title']} ({n.get('source','')}) — {n['link']}")
    return "\n".join(lines)


def send_digest_email(digest, dashboard_url=None):
    app_password = os.environ.get("GMAIL_APP_PASSWORD")
    if not app_password:
        print("GMAIL_APP_PASSWORD not set — skipping email send.")
        return

    date_str = datetime.utcnow().strftime("%B %d, %Y")
    account_count = len(digest)

    subject = f"Account Watch — {date_str} ({account_count} accounts with activity)"

    body = _plaintext_summary(digest)
    if dashboard_url:
        body += f"\n\nFull dashboard: {dashboard_url}\n"

    msg = MIMEMultipart()
    msg["From"] = GMAIL_ADDRESS
    msg["To"] = GMAIL_ADDRESS
    msg["Subject"] = subject
    msg.attach(MIMEText(body, "plain"))

    with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
        server.login(GMAIL_ADDRESS, app_password)
        server.sendmail(GMAIL_ADDRESS, [GMAIL_ADDRESS], msg.as_string())

    print("Digest email sent.")

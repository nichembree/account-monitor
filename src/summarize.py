"""Summarize each account's daily news + filings using Claude.

Requires an Anthropic API key set as the environment variable
ANTHROPIC_API_KEY. Get one at https://console.anthropic.com/settings/keys
(this is separate from a claude.ai subscription — it's pay-as-you-go API
usage, but summarizing ~50 short digests a day costs a few cents at most
with Haiku).
"""
import os
import requests

ANTHROPIC_API_URL = "https://api.anthropic.com/v1/messages"
MODEL = "claude-haiku-4-5-20251001"

SYSTEM_PROMPT = (
    "You summarize daily news and SEC filings for a B2B sales rep who sells "
    "industrial software into oil & gas and energy companies. Given a list of "
    "headlines, snippets, and filing types for one company, write a tight "
    "2-4 sentence summary of what's actually happening — prioritize things "
    "like expansions, capital projects, M&A, financial results, leadership "
    "changes, or operational incidents. Skip generic or irrelevant items. "
    "If nothing substantive is happening, say so in one short sentence. "
    "Do not use bullet points. Do not add a preamble like 'Here is a summary'."
)


def _build_prompt(account_name, news_items, filing_items):
    lines = [f"Company: {account_name}", ""]

    if filing_items:
        lines.append("SEC filings today:")
        for f in filing_items:
            lines.append(f"- {f.get('form','')} filed {f.get('filed','')}")
        lines.append("")

    if news_items:
        lines.append("News items today:")
        for n in news_items[:10]:  # cap to keep the prompt small and cheap
            snippet = n.get("snippet", "").strip()
            lines.append(f"- {n['title']} ({n.get('source','')}): {snippet}")

    return "\n".join(lines)


def summarize_account(account_name, news_items, filing_items):
    api_key = os.environ.get("ANTHROPIC_API_KEY")
    if not api_key:
        return None  # caller falls back to raw link list

    prompt = _build_prompt(account_name, news_items, filing_items)

    try:
        resp = requests.post(
            ANTHROPIC_API_URL,
            headers={
                "x-api-key": api_key,
                "anthropic-version": "2023-06-01",
                "content-type": "application/json",
            },
            json={
                "model": MODEL,
                "max_tokens": 300,
                "system": SYSTEM_PROMPT,
                "messages": [{"role": "user", "content": prompt}],
            },
            timeout=30,
        )
        resp.raise_for_status()
        data = resp.json()
        text_blocks = [b["text"] for b in data.get("content", []) if b.get("type") == "text"]
        return "".join(text_blocks).strip() or None
    except Exception as e:
        print(f"Summarization failed for {account_name}: {e}")
        return None

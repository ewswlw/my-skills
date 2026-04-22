"""
Perplexity HTTP API (https://api.perplexity.ai/chat/completions) first, then free fallbacks.

API key: set user/system env PERPLEXITY_API_KEY — the same variable as
`C:\\Users\\Eddy\\.cursor\\mcp.json` -> perplexity -> ${env:PERPLEXITY_API_KEY}.
Optional: skill-directory .env; see parent SKILL.md.
"""

from __future__ import annotations

import argparse
import json
import os
import re
import sys
import time
from pathlib import Path
from typing import Any

import httpx
from dotenv import load_dotenv

SKILL_ROOT = Path(__file__).resolve().parent.parent
ENV_PATH = SKILL_ROOT / ".env"

PPLX_URL = "https://api.perplexity.ai/chat/completions"
DDG_URL = "https://api.duckduckgo.com/"
# Public MediaWiki opensearch: best-effort snippets when DDG is empty. See https://www.mediawiki.org/wiki/API:Opensearch
WIKI_API = "https://en.wikipedia.org/w/api.php"
HTTP_USER_AGENT = "DeepResearchSkill/1.0 (httpx; personal research; +https://docs.perplexity.ai/)"

# Defaults align with project-spec
DEFAULT_PPLX_TIMEOUT = 120.0
DEFAULT_FALLBACK_TIMEOUT = 60.0
MAX_PERPLEXITY_RETRIES = 2
BACKOFF_SECS = (1.0, 3.0)
# sonar-deep-research may include internal reasoning blocks; strip for clean reports
_REDACTED_THINKING = re.compile(r"<think>.*?</think>\s*", re.DOTALL | re.IGNORECASE)


def _strip_internal_thinking(text: str) -> str:
    return _REDACTED_THINKING.sub("", text).strip()


def _load_env() -> None:
    load_dotenv(ENV_PATH)
    load_dotenv()  # cwd / process env


def _perplexity_payload(
    query: str,
    model: str,
    reasoning_effort: str | None,
) -> dict[str, Any]:
    system = (
        "You are a research assistant. Answer with clear structure, date-aware context, "
        "and numbered or inline citations to sources when available. If uncertain, say so."
    )
    body: dict[str, Any] = {
        "model": model,
        "messages": [
            {"role": "system", "content": system},
            {"role": "user", "content": query},
        ],
        "temperature": 0.2,
        "stream": False,
    }
    if model == "sonar-deep-research" and reasoning_effort:
        body["reasoning_effort"] = reasoning_effort
    return body


def _extract_perplexity_text(data: dict[str, Any]) -> str:
    choices = data.get("choices") or []
    if not choices:
        return ""
    msg = (choices[0] or {}).get("message") or {}
    raw = (msg.get("content") or "").strip()
    return _strip_internal_thinking(raw)


def call_perplexity(
    client: httpx.Client,
    query: str,
) -> tuple[str, dict[str, Any] | None, str | None]:
    key = (os.environ.get("PERPLEXITY_API_KEY") or "").strip()
    if not key:
        return "", None, "PERPLEXITY_API_KEY not set"

    model = (os.environ.get("PERPLEXITY_MODEL") or "sonar-deep-research").strip()
    effort = (os.environ.get("PERPLEXITY_REASONING_EFFORT") or "medium").strip()
    if model != "sonar-deep-research":
        effort = None
    pl = _perplexity_payload(query, model, effort)

    timeout = float(os.environ.get("DEEP_RESEARCH_PERPLEXITY_TIMEOUT", DEFAULT_PPLX_TIMEOUT))
    last_err: str | None = None

    for attempt in range(1 + MAX_PERPLEXITY_RETRIES):
        try:
            r = client.post(
                PPLX_URL,
                headers={"Authorization": f"Bearer {key}", "Content-Type": "application/json"},
                json=pl,
                timeout=timeout,
            )
            if r.status_code in (429, 500, 502, 503, 504) and attempt < MAX_PERPLEXITY_RETRIES:
                time.sleep(BACKOFF_SECS[min(attempt, len(BACKOFF_SECS) - 1)])
                last_err = f"HTTP {r.status_code}"
                continue
            r.raise_for_status()
            data = r.json()
            text = _extract_perplexity_text(data)
            return text, data, None if text else "empty response from Perplexity"
        except httpx.HTTPError as e:
            last_err = str(e)
            if attempt < MAX_PERPLEXITY_RETRIES:
                time.sleep(BACKOFF_SECS[min(attempt, len(BACKOFF_SECS) - 1)])
    return "", None, last_err or "Perplexity request failed"


def call_duckduckgo_instant_answer(
    client: httpx.Client,
    query: str,
) -> tuple[str, dict[str, Any] | None, str | None]:
    """
    Free, no-API-key fallback. Often sparse for complex questions; used only when Perplexity fails.
    See https://duckduckgo.com/api (community instant answer; not guaranteed).
    """
    timeout = float(os.environ.get("DEEP_RESEARCH_FALLBACK_TIMEOUT", DEFAULT_FALLBACK_TIMEOUT))
    try:
        r = client.get(
            DDG_URL,
            params={
                "q": query,
                "format": "json",
                "no_html": "1",
                "skip_disambig": "1",
            },
            timeout=timeout,
        )
        r.raise_for_status()
        data = r.json()
    except (httpx.HTTPError, json.JSONDecodeError) as e:
        return "", None, str(e)

    parts: list[str] = []
    abstract = (data.get("AbstractText") or "").strip()
    heading = (data.get("AbstractSource") or "").strip()
    if abstract:
        line = abstract
        if heading:
            line = f"({heading}) {line}"
        parts.append(line)

    for t in (data.get("RelatedTopics") or [])[:5]:
        if isinstance(t, dict) and t.get("Text"):
            parts.append(f"- {t['Text']}")

    text = "\n\n".join(parts).strip() or (data.get("Answer") or "").strip()
    if not text:
        return "", data, "DuckDuckGo returned no instant answer; try a shorter query or use Perplexity."
    return text, data, None


def call_wikipedia_opensearch(
    client: httpx.Client,
    query: str,
) -> tuple[str, dict[str, Any] | None, str | None]:
    """
    Free, no-API-key fallback: first few Wikipedia opensearch descriptions.
    Respects a descriptive User-Agent per Wikimedia guidance.
    """
    timeout = float(os.environ.get("DEEP_RESEARCH_FALLBACK_TIMEOUT", DEFAULT_FALLBACK_TIMEOUT))
    headers = {"User-Agent": HTTP_USER_AGENT}
    try:
        r = client.get(
            WIKI_API,
            params={
                "action": "opensearch",
                "search": query,
                "limit": 5,
                "namespace": 0,
                "format": "json",
            },
            headers=headers,
            timeout=timeout,
        )
        r.raise_for_status()
        data = r.json()
    except (httpx.HTTPError, json.JSONDecodeError, ValueError) as e:
        return "", None, str(e)

    # [searchterm, titles, descs, urls]
    if not isinstance(data, list) or len(data) < 4:
        return "", data, "Wikipedia opensearch: unexpected response shape"
    titles, descs, urls = data[1], data[2], data[3]
    if not titles:
        return "", data, "Wikipedia: no search hits"

    lines: list[str] = []
    for i, title in enumerate(titles):
        d = (descs[i] if i < len(descs) else "") or ""
        u = (urls[i] if i < len(urls) else "") or ""
        line = f"- **{title}**"
        if d:
            line += f" — {d}"
        if u:
            line += f" <{u}>"
        lines.append(line)
    body = "Best-effort snippets from English Wikipedia opensearch (verify at source pages):\n\n" + "\n".join(
        lines
    )
    return body, {"opensearch": data}, None


def _banner_line(source: str) -> str:
    return f"**Research source:** {source}"


def format_output_markdown(
    query: str,
    body: str,
    source_label: str,
) -> str:
    lines = [
        _banner_line(source_label),
        "",
        "## Question",
        query.strip(),
        "",
        "## Findings",
        body.strip(),
    ]
    return "\n".join(lines) + "\n"


def main() -> int:
    p = argparse.ArgumentParser(description="Deep research via Perplexity, then free DDG fallback.")
    p.add_argument("-q", "--query", required=True, help="Research question or topic")
    p.add_argument("--json", action="store_true", help="Print JSON to stdout (includes source + raw when available)")
    p.add_argument("--out", type=Path, help="Write markdown report to this path")
    args = p.parse_args()

    _load_env()
    q = args.query.strip()
    if not q:
        print("Empty query", file=sys.stderr)
        return 1

    with httpx.Client() as client:
        text, raw_pplx, pplx_err = call_perplexity(client, q)

    source = "Perplexity"
    raw: dict[str, Any] | None = raw_pplx
    err_final: str | None = pplx_err

    if not (text and text.strip()):
        with httpx.Client(headers={"User-Agent": HTTP_USER_AGENT}) as client:
            text, raw_ddg, ddg_err = call_duckduckgo_instant_answer(client, q)
        raw = raw_ddg
        err_final = ddg_err
        source = "Fallback — DuckDuckGo Instant Answer"

    if not (text and text.strip()):
        with httpx.Client(headers={"User-Agent": HTTP_USER_AGENT}) as client:
            text, raw_wiki, wiki_err = call_wikipedia_opensearch(client, q)
        if text and text.strip():
            raw = raw_wiki
            err_final = None
            source = "Fallback — Wikipedia opensearch (snippets)"
        else:
            raw = raw_wiki
            err_final = wiki_err or err_final

    if not (text and text.strip()):
        payload: dict[str, Any] = {
            "error": err_final or "No content from Perplexity or fallback",
            "research_source": None,
            "query": q,
        }
        print(json.dumps(payload, indent=2))
        return 1

    md = format_output_markdown(q, text, source)
    if args.json:
        out_obj: dict[str, Any] = {
            "research_source": source,
            "query": q,
            "content": text,
        }
        if raw is not None:
            out_obj["raw"] = raw
        print(json.dumps(out_obj, indent=2))
    else:
        print(md, end="")
    if args.out:
        args.out.parent.mkdir(parents=True, exist_ok=True)
        args.out.write_text(md, encoding="utf-8")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())

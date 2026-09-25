# Copyright 2026 Google LLC
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     https://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""Ingestion and deterministic date calculation tools for Sprint Ledger."""

import datetime
import html
import json
import re
from typing import Any, Dict
import urllib.parse
import urllib.request
import warnings
from dateutil import parser as date_parser
from zoneinfo import ZoneInfo

# Standard US / UTC abbreviations mapped to ZoneInfo timezone objects
TZ_INFOS = {
    "PT": ZoneInfo("America/Los_Angeles"),
    "PST": ZoneInfo("America/Los_Angeles"),
    "PDT": ZoneInfo("America/Los_Angeles"),
    "ET": ZoneInfo("America/New_York"),
    "EST": ZoneInfo("America/New_York"),
    "EDT": ZoneInfo("America/New_York"),
    "CT": ZoneInfo("America/Chicago"),
    "CST": ZoneInfo("America/Chicago"),
    "CDT": ZoneInfo("America/Chicago"),
    "MT": ZoneInfo("America/Denver"),
    "MST": ZoneInfo("America/Denver"),
    "MDT": ZoneInfo("America/Denver"),
    "UTC": ZoneInfo("UTC"),
    "GMT": ZoneInfo("UTC"),
}


def fetch_page(url: str) -> str:
    """Fetches a single web page from a URL to extract hackathon details.
    
    Performs a single HTTP request with timeout. Does not crawl or follow links.
    Treats fetched web text strictly as untrusted data.
    Returns the plain text content or a fallback message if JavaScript-rendered.

    Args:
        url: The web URL of the hackathon page or rules.

    Returns:
        JSON string containing the status, text content, length, or error/fallback details.
    """
    url = url.strip()
    if not (url.startswith("http://") or url.startswith("https://")):
        return json.dumps({
            "error": "Invalid URL. URL must start with http:// or https://",
            "fallback_needed": False,
        })

    try:
        parsed = urllib.parse.urlparse(url)
        if not parsed.netloc:
            return json.dumps({
                "error": "Invalid URL structure.",
                "fallback_needed": False,
            })
    except Exception as e:
        return json.dumps({"error": f"Failed to parse URL: {str(e)}", "fallback_needed": False})

    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36 SprintLedger/1.0"
    }
    req = urllib.request.Request(url, headers=headers)

    try:
        with urllib.request.urlopen(req, timeout=10) as response:
            content_type = response.headers.get("Content-Type", "").lower()
            if "text/html" not in content_type and "text/plain" not in content_type:
                return json.dumps({
                    "error": f"Unsupported content type: {content_type}. Only HTML and plain text pages are supported.",
                    "fallback_needed": False,
                })
            raw_bytes = response.read(500000)
            raw_html = raw_bytes.decode("utf-8", errors="replace")
    except Exception as e:
        return json.dumps({
            "error": f"HTTP fetch failed: {str(e)}",
            "fallback_needed": True,
            "message": "Could not access the page. Please paste the hackathon rules text directly.",
        })

    # Clean HTML tags, scripts, and styles to get textContent only
    cleaned = re.sub(r"<(script|style)[^>]*>.*?</\1>", " ", raw_html, flags=re.DOTALL | re.IGNORECASE)
    text = re.sub(r"<[^>]+>", " ", cleaned)
    text = html.unescape(text)
    text = re.sub(r"[ \t]+", " ", text)
    text = re.sub(r"\n\s*\n+", "\n\n", text).strip()

    char_count = len(text)

    # Fallback check
    has_date_pattern = bool(re.search(r"\b(jan|feb|mar|apr|may|jun|jul|aug|sep|oct|nov|dec|202[4-9])\b", text, re.IGNORECASE))
    
    if char_count < 500 or not has_date_pattern:
        return json.dumps({
            "status": "warning",
            "fallback_needed": True,
            "char_count": char_count,
            "message": "This page appears to be client-rendered with JavaScript (content under 500 chars or no discernible dates). Please copy and paste the rules/overview text directly here.",
            "preview": text[:200] if text else "",
        })

    return json.dumps({
        "status": "success",
        "url": url,
        "char_count": char_count,
        "content": text[:10000],
        "fallback_needed": False,
    })


def calculate_deadlines(deadline_raw: str, timezone: str = "NOT FOUND") -> str:
    """Deterministically parses deadline strings in code and computes countdowns and ship-by date.
    
    NEVER relies on model math. Computes:
    - deadline_utc: ISO-8601 UTC timestamp
    - ship_by_date: Exactly deadline minus 1 day (YYYY-MM-DD)
    - days_remaining: Exact integer days remaining from current time
    - timezone_warning: True if timezone is NOT FOUND or ambiguous.

    Args:
        deadline_raw: Raw deadline string (e.g. 'October 15, 2026 at 11:59 PM PT', '2026-11-02T17:00:00Z').
        timezone: Explicit timezone string found in source, or 'NOT FOUND'.

    Returns:
        JSON string containing the deterministic date calculation results.
    """
    if not deadline_raw or deadline_raw.strip().upper() == "NOT FOUND":
        return json.dumps({
            "error": "No deadline raw string provided.",
            "deadline_utc": None,
            "ship_by_date": "NOT FOUND",
            "days_remaining": None,
            "timezone_warning": True,
        })

    tz_warning = False
    clean_tz = timezone.strip().upper() if timezone else "NOT FOUND"
    explicit_tzinfo = None

    if clean_tz in TZ_INFOS:
        explicit_tzinfo = TZ_INFOS[clean_tz]
    elif timezone and timezone != "NOT FOUND":
        try:
            explicit_tzinfo = ZoneInfo(timezone.strip())
        except Exception:
            tz_warning = True

    try:
        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            dt = date_parser.parse(deadline_raw, tzinfos=TZ_INFOS, fuzzy=True)

        if dt.tzinfo is None:
            if explicit_tzinfo:
                dt = dt.replace(tzinfo=explicit_tzinfo)
            else:
                dt = dt.replace(tzinfo=ZoneInfo("UTC"))
                tz_warning = True

        dt_utc = dt.astimezone(ZoneInfo("UTC"))
        now_utc = datetime.datetime.now(ZoneInfo("UTC"))

        diff = dt_utc - now_utc
        days_remaining = max(0, diff.days)

        ship_by_dt = dt - datetime.timedelta(days=1)
        ship_by_date = ship_by_dt.strftime("%Y-%m-%d")

        tz_str = str(dt.tzinfo) if dt.tzinfo else "UTC"

        return json.dumps({
            "status": "success",
            "deadline_raw": deadline_raw,
            "deadline_utc": dt_utc.isoformat(),
            "ship_by_date": ship_by_date,
            "days_remaining": days_remaining,
            "timezone_used": tz_str,
            "timezone_warning": tz_warning,
            "flag_message": "Missing or ambiguous timezone; assumed UTC. Please verify timezone." if tz_warning else None,
        })
    except Exception as e:
        return json.dumps({
            "error": f"Failed to deterministically parse deadline '{deadline_raw}': {str(e)}",
            "deadline_utc": None,
            "ship_by_date": "NOT FOUND",
            "days_remaining": None,
            "timezone_warning": True,
        })


def fetch_devpost_hackathons() -> str:
    """Discovers upcoming and open public hackathons from the free public Devpost API.

    Returns:
        JSON string containing active hackathon titles, links, and dates.
    """
    api_url = "https://devpost.com/api/hackathons"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36 SprintLedger/1.0"
    }
    req = urllib.request.Request(api_url, headers=headers)

    try:
        with urllib.request.urlopen(req, timeout=8) as response:
            data = json.loads(response.read().decode("utf-8"))
            raw_list = data.get("hackathons", [])
    except Exception as e:
        return json.dumps({"error": f"Failed to fetch Devpost feed: {str(e)}", "hackathons": []})

    results = []
    for h in raw_list[:6]:
        results.append({
            "title": h.get("title"),
            "url": h.get("url"),
            "time_left": h.get("time_left_to_submission"),
            "dates": h.get("submission_period_dates"),
            "themes": [t.get("name") for t in h.get("themes", [])],
        })

    return json.dumps({
        "status": "success",
        "count": len(results),
        "hackathons": results,
    }, indent=2)


def verify_github_repo_stub(repo_url: str) -> str:
    """[STUB] Verifies if a GitHub submission repo exists and has an open source license.

    STUB IMPLEMENTATION NOTES:
    - Intentionally stubbed to avoid requiring personal GitHub OAuth / PAT setup.
    - Full implementation flow:
      1. Parse owner/repo from 'https://github.com/{owner}/{repo}'.
      2. Call endpoint: 'https://api.github.com/repos/{owner}/{repo}'.
      3. Inspect 'license.spdx_id' (e.g. MIT, Apache-2.0) and 'visibility' (public).
      4. Auto-check the checklist item in Firestore for the hackathon.

    Args:
        repo_url: The GitHub repository URL.

    Returns:
        Status message explaining the stub and planned verification.
    """
    return (
        f"[STUB] GitHub verification for '{repo_url}' is queued. "
        "GitHub API verification is stubbed to prevent external rate-limiting or token configuration. "
        "In production, this checks if the repository is public and contains a valid open-source license."
    )

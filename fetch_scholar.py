"""Fetch Google Scholar metrics and per-paper citations (via SerpAPI) into metrics.json."""
import json
import os
import sys
import urllib.parse
import urllib.request
from datetime import datetime, timezone

USER_ID = "ggyjcXoAAAAJ"
PROFILE_URL = f"https://scholar.google.com/citations?user={USER_ID}&hl=en"
API_KEY = os.environ.get("SERPAPI_KEY")


def call(start):
    params = {
        "engine": "google_scholar_author",
        "author_id": USER_ID,
        "hl": "en",
        "num": 100,
        "start": start,
        "api_key": API_KEY,
    }
    url = "https://serpapi.com/search.json?" + urllib.parse.urlencode(params)
    with urllib.request.urlopen(url, timeout=60) as resp:
        return json.load(resp)


def table_value(table, key):
    for row in table or []:
        if key in row:
            return row[key].get("all")
    return None


def main():
    if not API_KEY:
        print("SERPAPI_KEY is not set", file=sys.stderr)
        sys.exit(1)
    articles, first, start = [], None, 0
    while True:
        page = call(start)
        if page.get("error"):
            print("SerpAPI error:", page["error"], file=sys.stderr)
            sys.exit(1)
        first = first or page
        articles += page.get("articles", [])
        if not page.get("serpapi_pagination", {}).get("next"):
            break
        start += 100
    table = first.get("cited_by", {}).get("table", [])
    pubs = []
    for a in articles:
        cb = a.get("cited_by") or {}
        n = cb.get("value") or 0
        pubs.append({
            "title": a.get("title", ""),
            "year": a.get("year"),
            "citations": n,
            "scholar_url": a.get("link"),
            "cited_by_url": cb.get("link") if n else None,
        })
    total = table_value(table, "citations")
    if not pubs or total is None:
        print("No data returned; keeping previous metrics.json", file=sys.stderr)
        sys.exit(1)
    data = {
        "updated": datetime.now(timezone.utc).strftime("%Y-%m-%d"),
        "profile_url": PROFILE_URL,
        "citations": total,
        "h_index": table_value(table, "h_index"),
        "i10_index": table_value(table, "i10_index"),
        "publications": pubs,
    }
    with open("metrics.json", "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
    print(f"Saved {len(pubs)} publications; {total} citations")


if __name__ == "__main__":
    main()

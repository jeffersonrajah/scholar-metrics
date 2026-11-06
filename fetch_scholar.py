"""Fetch Google Scholar metrics and per-paper citations into metrics.json."""
import json
import sys
from datetime import datetime, timezone

from scholarly import scholarly

USER_ID = "ggyjcXoAAAAJ"
PROFILE_URL = f"https://scholar.google.com/citations?user={USER_ID}&hl=en"


def cited_by_url(pub):
    """Link to the list of works citing this paper on Google Scholar."""
    cites_id = pub.get("cites_id")
    if cites_id:
        return f"https://scholar.google.com/scholar?hl=en&cites={cites_id[0]}"
    url = pub.get("citedby_url")
    if url:
        return "https://scholar.google.com" + url if url.startswith("/") else url
    return None


def main():
    author = scholarly.search_author_id(USER_ID)
    author = scholarly.fill(author, sections=["basics", "indices", "counts", "publications"])
    pubs = []
    for p in author.get("publications", []):
        bib = p.get("bib", {})
        pid = p.get("author_pub_id", "")
        pubs.append({
            "title": bib.get("title", ""),
            "year": bib.get("pub_year"),
            "citations": p.get("num_citations", 0),
            "scholar_url": f"https://scholar.google.com/citations?view_op=view_citation&hl=en&user={USER_ID}&citation_for_view={pid}" if pid else None,
            "cited_by_url": cited_by_url(p) if p.get("num_citations", 0) else None,
        })
    if not pubs or not author.get("citedby"):
        print("No data returned; keeping previous metrics.json", file=sys.stderr)
        sys.exit(1)
    data = {
        "updated": datetime.now(timezone.utc).strftime("%Y-%m-%d"),
        "profile_url": PROFILE_URL,
        "citations": author.get("citedby"),
        "h_index": author.get("hindex"),
        "i10_index": author.get("i10index"),
        "publications": pubs,
    }
    with open("metrics.json", "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
    print(f"Saved {len(pubs)} publications; {data['citations']} citations")


if __name__ == "__main__":
    main()

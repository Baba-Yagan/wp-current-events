import requests
import os
from datetime import datetime
from urllib.parse import urlparse, parse_qs

def fetch_wikipedia_textarea(url):
    """Fetch wikitext content for a page via the Wikipedia API.

    The edit-page scrape (wpTextbox1 textarea) no longer works: Wikipedia
    serves protected pages as "view source" with no textarea for anonymous
    users. Use the API instead; `url` is only parsed for the page title.
    """
    print(f"Requesting URL: {url}")
    headers = {
        "User-Agent": "wp-current-events/1.0 (https://github.com/Baba-Yagan/wp-current-events)"
    }

    parsed_url = urlparse(url)
    query_params = parse_qs(parsed_url.query)
    title = query_params.get('title', ['unknown'])[0]

    resp = requests.get(
        "https://en.wikipedia.org/w/api.php",
        params={
            "action": "query",
            "prop": "revisions",
            "titles": title,
            "rvprop": "content",
            "rvslots": "main",
            "format": "json",
            "formatversion": "2",
        },
        headers=headers,
        timeout=15,
    )
    resp.raise_for_status()

    data = resp.json()
    pages = data.get("query", {}).get("pages", [])
    if not pages or "missing" in pages[0]:
        return None

    revisions = pages[0].get("revisions", [])
    if not revisions:
        return None

    return revisions[0]["slots"]["main"]["content"]

if __name__ == "__main__":
    url = "https://en.wikipedia.org/w/index.php?title=Portal:Current_events/2025_September_19&action=edit&editintro=Portal:Current_events/Edit_instructions"
    content = fetch_wikipedia_textarea(url)
    print(content)

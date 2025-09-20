import requests
from fetch_wiki import fetch_wikipedia_textarea

# Fetch wikitext from Wikipedia edit page
url = "https://en.wikipedia.org/w/index.php?title=Portal:Current_events/2025_September_19&action=edit&editintro=Portal:Current_events/Edit_instructions"
wikitext = fetch_wikipedia_textarea(url)

headers = {
"User-Agent": "wp-current-events/1.0 (https://github.com/Baba-Yagan/wp-current-events)"
}

resp = requests.post(
    "https://en.wikipedia.org/w/api.php",
    params={"action":"parse","format":"json","contentmodel":"wikitext"},
    data={"text": wikitext},
    headers=headers,
    timeout=10
)

resp.raise_for_status()
data = resp.json()
html = data["parse"]["text"]["*"]
print(html)

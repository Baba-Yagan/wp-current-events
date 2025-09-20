import requests

wikitext = "==Title==\nThis is '''bold''' text."

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

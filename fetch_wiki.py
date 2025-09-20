import requests
from lxml import html

def fetch_wikipedia_textarea(url):
    """Fetch content from Wikipedia edit page textarea"""
    headers = {
        "User-Agent": "wp-current-events/1.0 (https://github.com/Baba-Yagan/wp-current-events)"
    }
    
    resp = requests.get(url, headers=headers, timeout=10)
    resp.raise_for_status()
    
    tree = html.fromstring(resp.content)
    textarea_content = tree.xpath('//*[@id="wpTextbox1"]')[0].text
    
    return textarea_content

if __name__ == "__main__":
    url = "https://en.wikipedia.org/w/index.php?title=Portal:Current_events/2025_September_19&action=edit&editintro=Portal:Current_events/Edit_instructions"
    content = fetch_wikipedia_textarea(url)
    print(content)

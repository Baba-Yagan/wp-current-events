import requests
from lxml import html
import os
from datetime import datetime
from urllib.parse import urlparse, parse_qs

def fetch_wikipedia_textarea(url):
    """Fetch content from Wikipedia edit page textarea"""
    print(f"Requesting URL: {url}")
    headers = {
        "User-Agent": "wp-current-events/1.0 (https://github.com/Baba-Yagan/wp-current-events)"
    }
    
    resp = requests.get(url, headers=headers, timeout=10)
    resp.raise_for_status()
    
    # # Create result directory if it doesn't exist
    # os.makedirs("result", exist_ok=True)
    
    # Extract date from URL for filename
    parsed_url = urlparse(url)
    query_params = parse_qs(parsed_url.query)
    title = query_params.get('title', ['unknown'])[0]
    
    # # Create filename from title and timestamp
    # timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    # safe_title = title.replace(':', '_').replace('/', '_')
    # filename = f"result/{safe_title}_{timestamp}.html"
    
    # # Save full HTML response
    # with open(filename, 'w', encoding='utf-8') as f:
    #     f.write(resp.text)
    
    tree = html.fromstring(resp.content)
    textarea_content = tree.xpath('//*[@id="wpTextbox1"]')[0].text
    
    # print(f"Saved full response to {filename}")
    return textarea_content

if __name__ == "__main__":
    url = "https://en.wikipedia.org/w/index.php?title=Portal:Current_events/2025_September_19&action=edit&editintro=Portal:Current_events/Edit_instructions"
    content = fetch_wikipedia_textarea(url)
    print(content)

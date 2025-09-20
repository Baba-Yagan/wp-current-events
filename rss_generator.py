import requests
import xml.etree.ElementTree as ET
from datetime import datetime, timedelta
from fetch_wiki import fetch_wikipedia_textarea
from email.utils import formatdate
import time

def parse_wikitext_to_html(wikitext):
    """Parse wikitext to HTML using Wikipedia API"""
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
    return data["parse"]["text"]["*"]

def generate_wikipedia_url(date):
    """Generate Wikipedia current events URL for a given date"""
    date_str = date.strftime("%Y_%B_%d")
    return f"https://en.wikipedia.org/w/index.php?title=Portal:Current_events/{date_str}&action=edit&editintro=Portal:Current_events/Edit_instructions"

def create_rss_feed(items, title="Wikipedia Current Events", description="Current events from Wikipedia"):
    """Create RSS feed XML from items"""
    rss = ET.Element("rss", version="2.0")
    channel = ET.SubElement(rss, "channel")
    
    ET.SubElement(channel, "title").text = title
    ET.SubElement(channel, "description").text = description
    ET.SubElement(channel, "link").text = "https://en.wikipedia.org/wiki/Portal:Current_events"
    ET.SubElement(channel, "lastBuildDate").text = formatdate(time.time())
    
    for item_data in items:
        item = ET.SubElement(channel, "item")
        ET.SubElement(item, "title").text = item_data["title"]
        ET.SubElement(item, "description").text = item_data["description"]
        ET.SubElement(item, "link").text = item_data["link"]
        ET.SubElement(item, "pubDate").text = item_data["pubDate"]
        ET.SubElement(item, "guid").text = item_data["link"]
    
    return ET.tostring(rss, encoding="unicode")

def generate_current_events_rss(days=7):
    """Generate RSS feed for Wikipedia current events for the last X days"""
    items = []
    
    for i in range(days):
        date = datetime.now() - timedelta(days=i)
        url = generate_wikipedia_url(date)
        
        try:
            print(f"Fetching content for {date.strftime('%Y-%m-%d')}...")
            wikitext = fetch_wikipedia_textarea(url)
            
            if wikitext and wikitext.strip():
                html_content = parse_wikitext_to_html(wikitext)
                
                item = {
                    "title": f"Current Events - {date.strftime('%B %d, %Y')}",
                    "description": html_content,
                    "link": f"https://en.wikipedia.org/wiki/Portal:Current_events/{date.strftime('%Y_%B_%d')}",
                    "pubDate": formatdate(time.mktime(date.timetuple()))
                }
                items.append(item)
                print(f"Successfully processed {date.strftime('%Y-%m-%d')}")
            else:
                print(f"No content found for {date.strftime('%Y-%m-%d')}")
                
        except Exception as e:
            print(f"Error processing {date.strftime('%Y-%m-%d')}: {e}")
            continue
    
    return create_rss_feed(items)

if __name__ == "__main__":
    import sys
    
    days = 7
    if len(sys.argv) > 1:
        try:
            days = int(sys.argv[1])
        except ValueError:
            print("Invalid number of days, using default of 7")
    
    print(f"Generating RSS feed for the last {days} days...")
    rss_xml = generate_current_events_rss(days)
    
    with open("current_events.rss", "w", encoding="utf-8") as f:
        f.write(rss_xml)
    
    print("RSS feed saved to current_events.rss")

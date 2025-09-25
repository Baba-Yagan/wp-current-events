import requests
import xml.etree.ElementTree as ET
from datetime import datetime, timedelta
from fetch_wiki import fetch_wikipedia_textarea
from email.utils import formatdate
import time
import json
import os
import re

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
    html_content = data["parse"]["text"]["*"]
    
    # Strip HTML comments
    html_content = re.sub(r'<!--.*?-->', '', html_content, flags=re.DOTALL)
    
    # Replace relative Wikipedia links with absolute links to English Wikipedia
    html_content = re.sub(r'href="/wiki/', r'href="https://en.wikipedia.org/wiki/', html_content)
    html_content = re.sub(r'href="/w/', r'href="https://en.wikipedia.org/w/', html_content)
    
    return html_content

def load_fetched_dates(filename="fetched_dates.json"):
    """Load previously fetched dates from JSON file"""
    if os.path.exists(filename):
        try:
            with open(filename, "r") as f:
                data = json.load(f)
                # Convert string dates back to datetime objects, normalize to date only
                return {datetime.fromisoformat(date).date(): fetched_time for date, fetched_time in data.items()}
        except (json.JSONDecodeError, ValueError):
            return {}
    return {}

def save_fetched_dates(fetched_dates, filename="fetched_dates.json"):
    """Save fetched dates to JSON file"""
    # Convert date objects to ISO format strings
    data = {date.isoformat(): fetched_time for date, fetched_time in fetched_dates.items()}
    with open(filename, "w") as f:
        json.dump(data, f, indent=2)

def should_fetch_date(date, fetched_dates):
    """Determine if a date should be fetched based on age and previous fetch time"""
    now = datetime.now()
    date_only = date.date()
    days_old = (now.date() - date_only).days
    
    # Always fetch if we haven't fetched this date before
    if date_only not in fetched_dates:
        return True
    
    # Don't update if the date is more than 2 days old AND we've already fetched it
    if days_old > 2:
        return False
    
    # For dates 2 days old or newer, always update
    return True

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

def load_existing_rss_items(filename="current_events.rss"):
    """Load existing RSS items from file"""
    if not os.path.exists(filename):
        return []
    
    try:
        tree = ET.parse(filename)
        root = tree.getroot()
        items = []
        
        for item in root.findall(".//item"):
            title_elem = item.find("title")
            desc_elem = item.find("description")
            link_elem = item.find("link")
            pubdate_elem = item.find("pubDate")
            
            if all(elem is not None for elem in [title_elem, desc_elem, link_elem, pubdate_elem]):
                items.append({
                    "title": title_elem.text,
                    "description": desc_elem.text,
                    "link": link_elem.text,
                    "pubDate": pubdate_elem.text
                })
        
        return items
    except ET.ParseError:
        return []

def generate_current_events_rss(days=7):
    """Generate RSS feed for Wikipedia current events for the last X days"""
    fetched_dates = load_fetched_dates()
    existing_items = load_existing_rss_items()
    new_items = []
    updated_fetched_dates = fetched_dates.copy()
    
    # Find dates that need fetching
    dates_to_fetch = []
    for i in range(days):
        date = datetime.now() - timedelta(days=i)
        if should_fetch_date(date, fetched_dates):
            dates_to_fetch.append(date)
    
    if not dates_to_fetch:
        print("No dates need updating. Using existing RSS content.")
        return create_rss_feed(existing_items)
    
    print(f"Need to fetch {len(dates_to_fetch)} dates: {[d.strftime('%Y-%m-%d') for d in dates_to_fetch]}")
    
    for date in dates_to_fetch:
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
                new_items.append(item)
                updated_fetched_dates[date.date()] = time.time()
                print(f"Successfully processed {date.strftime('%Y-%m-%d')}")
            else:
                print(f"No content found for {date.strftime('%Y-%m-%d')}")
                
        except Exception as e:
            print(f"Error processing {date.strftime('%Y-%m-%d')}: {e}")
            continue
    
    # Merge new items with existing items, removing duplicates by link
    all_items = new_items.copy()
    existing_links = {item["link"] for item in new_items}
    
    for existing_item in existing_items:
        if existing_item["link"] not in existing_links:
            all_items.append(existing_item)
    
    # Sort by date (newest first)
    all_items.sort(key=lambda x: x["pubDate"], reverse=True)
    
    # Save updated fetch tracking
    save_fetched_dates(updated_fetched_dates)
    
    return create_rss_feed(all_items)

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

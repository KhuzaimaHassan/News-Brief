import requests
import feedparser
import time

BASE_URL = "http://localhost:5000"

def seed_style():
    print("=== SEEDING BRIEFING STYLE ===")
    with open("../briefing-style.md", "r", encoding="utf-8") as f:
        style_content = f.read()
    
    # We must prepend STYLE RULE so app.py can find it using its filter
    full_style = "STYLE RULE:\n" + style_content
    
    # We don't have a dedicated /save_style endpoint, so we use the DB directly
    from db import memory
    thread = memory.create_thread(user_id="casius")
    thread.add_memory(full_style)
    print("Style seeded successfully!")

def seed_sources():
    print("\n=== SEEDING SOURCES ===")
    with open("../sources.md", "r", encoding="utf-8") as f:
        lines = f.readlines()
        
    urls = [line.strip() for line in lines if line.strip().startswith("https://")]
    print(f"Found {len(urls)} feeds to process.")
    
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8"
    }

    for url in urls:
        print(f"\nProcessing feed: {url}")
        try:
            res = requests.get(url, headers=headers, timeout=10)
            feed = feedparser.parse(res.content)
            entries = feed.entries[:2]
            print(f"Found {len(entries)} top entries.")
            
            for entry in entries:
                title = entry.get("title", "")
                link = entry.get("link", "")
                content = entry.get("summary", "")
                print(f" -> Summarizing: {title}")
                
                # Call /summarise
                sum_res = requests.post(f"{BASE_URL}/summarise", json={"title": title, "link": link, "content": content})
                if sum_res.status_code != 200:
                    print(f"    ERROR summarizing: {sum_res.text}")
                    continue
                
                summary = sum_res.json().get("summary", "")
                
                # Call /save
                print(f" -> Saving to memory...")
                save_res = requests.post(f"{BASE_URL}/save", json={"headline": title, "summary": summary})
                if save_res.status_code != 200:
                    print(f"    ERROR saving: {save_res.text}")
                    continue
                
                print("    Saved successfully.")
                time.sleep(1) # Small delay to be polite to the DB
                
        except Exception as e:
            print(f"Error processing {url}: {e}")

if __name__ == "__main__":
    seed_style()
    seed_sources()
    print("\n=== SEEDING COMPLETE ===")

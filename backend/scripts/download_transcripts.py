"""
Download transcripts from the public Lenny's Podcast Transcripts repository:
https://github.com/ChatPRD/lennys-podcast-transcripts
"""
import os
import sys
import httpx
import asyncio
from pathlib import Path

TRANSCRIPTS_DIR = Path(__file__).resolve().parent.parent / "data" / "transcripts"

# Representative high-impact episodes available in raw github format
CURATED_SOURCES = [
    {
        "slug": "elena-verna-plg",
        "title": "Elena Verna on B2B Product-Led Growth, Product-Led Sales, and Freemium Loops",
        "guest": "Elena Verna",
        "url": "https://raw.githubusercontent.com/ChatPRD/lennys-podcast-transcripts/main/transcripts/elena-verna.md"
    },
    {
        "slug": "shreyas-doshi-lno",
        "title": "Shreyas Doshi on The LNO Framework, High-Agency Product Leadership, and Career Strategy",
        "guest": "Shreyas Doshi",
        "url": "https://raw.githubusercontent.com/ChatPRD/lennys-podcast-transcripts/main/transcripts/shreyas-doshi.md"
    },
    {
        "slug": "brian-chesky-founder-mode",
        "title": "Brian Chesky on Founder Mode, Leading Airbnb, and Building Design-Driven Products",
        "guest": "Brian Chesky",
        "url": "https://raw.githubusercontent.com/ChatPRD/lennys-podcast-transcripts/main/transcripts/brian-chesky.md"
    }
]

async def download_curated_transcripts():
    TRANSCRIPTS_DIR.mkdir(parents=True, exist_ok=True)
    print(f"[*] Downloading transcripts to: {TRANSCRIPTS_DIR}")

    async with httpx.AsyncClient(timeout=30.0) as client:
        for item in CURATED_SOURCES:
            file_path = TRANSCRIPTS_DIR / f"{item['slug']}.md"
            if file_path.exists():
                print(f"[-] Already exists: {file_path.name}")
                continue

            print(f"[+] Fetching: {item['title']}...")
            try:
                res = await client.get(item["url"])
                if res.status_code == 200:
                    with open(file_path, "w", encoding="utf-8") as f:
                        f.write(res.text)
                    print(f"[✓] Saved {file_path.name}")
                else:
                    print(f"[!] HTTP {res.status_code} fetching {item['url']}")
            except Exception as e:
                print(f"[!] Network error downloading {item['title']}: {e}")

if __name__ == "__main__":
    asyncio.run(download_curated_transcripts())

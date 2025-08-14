
from typing import List, Dict, Optional
from youtubesearchpython import VideosSearch

def is_url(s: str) -> bool:
    return s.startswith("http://") or s.startswith("https://")

def search_youtube(query: str, limit: int = 8) -> List[Dict]:
    vs = VideosSearch(query, limit=limit)
    results = vs.result().get("result", [])
    # Normalize fields for display/selection
    normalized = []
    for r in results:
        normalized.append({
            "title": r.get("title"),
            "duration": r.get("duration"),
            "channel": (r.get("channel", {}) or {}).get("name"),
            "link": r.get("link"),
            "viewCount": (r.get("viewCount", {}) or {}).get("text"),
            "publishedTime": r.get("publishedTime"),
        })
    return normalized

def select_result(results: List[Dict]) -> Optional[Dict]:
    if not results:
        print("No results.")
        return None
    print("\nSearch results:")
    for i, r in enumerate(results, 1):
        print(f"[{i}] {r['title']}  | {r['channel']}  | {r['duration']}  | {r['viewCount']}")
    while True:
        s = input("Pick a number (or blank to cancel): ").strip()
        if not s:
            return None
        try:
            idx = int(s)
            if 1 <= idx <= len(results):
                return results[idx-1]
        except ValueError:
            pass
        print("Invalid choice.")

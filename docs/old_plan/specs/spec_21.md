# Spec 21 – Retrieve YouTube thumbnails

The application retrieves up to four video thumbnails related to a query using the YouTube Data API.  Since API usage is limited, provide graceful degradation when quotas are exceeded.

## Backend Function

```python
import os
import httpx

YOUTUBE_API_KEY = os.environ.get("YOUTUBE_API_KEY")

async def fetch_youtube_thumbnails(query: str, max_results: int = 4) -> list[dict]:
    if not YOUTUBE_API_KEY:
        return []
    search_url = (
        "https://www.googleapis.com/youtube/v3/search"
        f"?part=snippet&type=video&maxResults={max_results}&q={query}&key={YOUTUBE_API_KEY}"
    )
    async with httpx.AsyncClient() as client:
        try:
            resp = await client.get(search_url, timeout=10)
            resp.raise_for_status()
            data = resp.json()
            results = []
            for item in data.get("items", []):
                video_id = item["id"]["videoId"]
                title = item["snippet"]["title"]
                thumbnail_url = item["snippet"]["thumbnails"]["medium"]["url"]
                results.append({
                    "url": f"https://www.youtube.com/watch?v={video_id}",
                    "title": title,
                    "thumbnail_url": thumbnail_url,
                })
            return results
        except Exception as e:
            logger.error(f"YouTube API error: {e}")
            return []
```

## Error Handling and Fallback

If the API key is missing or the quota is exceeded, return an empty list.  The UI should detect an empty list and hide the YouTube section instead of displaying broken images.

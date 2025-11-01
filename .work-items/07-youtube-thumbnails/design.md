# Design: YouTube Thumbnails

## Objective
Display related YouTube videos using YouTube Data API v3.

## Technical Design
- Use YouTube Data API `search.list` endpoint
- Query: user's search query
- Max results: 4
- Return: video ID, title, thumbnail URL

## API Integration
```python
from googleapiclient.discovery import build

youtube = build('youtube', 'v3', developerKey=API_KEY)
request = youtube.search().list(
    q=query,
    part='snippet',
    maxResults=4,
    type='video'
)
```

## Out of Scope
- Video playback in UI
- Playlist support
- Channel filtering

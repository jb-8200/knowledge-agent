# Task 21 – Retrieve YouTube thumbnails

**Phase:** Additional Features

**Description:**

Implement functionality to fetch up to four YouTube video thumbnails relevant to the user’s query.  Use the YouTube Data API (`search.list` and `videos.list` endpoints) with the `YOUTUBE_API_KEY`.  Construct a backend function that sends a search request based on the query, selects the top results and extracts the thumbnail URLs.  Handle API rate limits and provide a fallback (e.g., an empty list) when the quota is exceeded or no results are found.  Return the thumbnails and associated video URLs in the response payload.

**Acceptance Criteria:**

* The YouTube API key is loaded from the environment and used securely.
* A function exists that returns up to four thumbnails and video URLs for a given query.
* Errors from the YouTube API are caught and handled gracefully without crashing the service.
* Unit tests mock YouTube API responses and verify correct extraction of thumbnail data and fallback behavior.

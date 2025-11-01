# Spec 04 – Implement a link ingestion endpoint

This specification covers the REST endpoint for ingesting web pages via their URLs.

## Endpoint Definition

Add a `POST /upload/link` endpoint that accepts a JSON payload containing a URL:

```python
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, HttpUrl
import uuid

app = FastAPI()

class LinkPayload(BaseModel):
    url: HttpUrl

@app.post("/upload/link")
async def upload_link(payload: LinkPayload, background_tasks: BackgroundTasks = None):
    url = str(payload.url)
    # Generate an ingestion ID
    ingestion_id = f"link_{uuid.uuid4()}"
    # Enqueue Firecrawl fetch and ingestion
    if background_tasks:
        background_tasks.add_task(fetch_and_ingest_link, url, ingestion_id)
    else:
        fetch_and_ingest_link(url, ingestion_id)
    return {"status": "accepted", "ingestion_id": ingestion_id}

```

`fetch_and_ingest_link` should use Firecrawl to fetch the page content and then pass the extracted text to the ingestion pipeline (parsing, chunking and embedding).  Validate the URL using Pydantic’s `HttpUrl` type; invalid URLs will result in a 422 error automatically.

## Firecrawl Integration

Implement the `fetch_and_ingest_link` function to call Firecrawl’s API:

```python
import httpx
import os

async def fetch_and_ingest_link(url: str, ingestion_id: str):
    api_key = os.environ.get("FIRECRAWL_API_KEY")
    try:
        # Example Firecrawl call; adjust endpoint and headers as needed
        resp = await httpx.get(
            f"https://firecrawl.dev/api/extract?url={url}",
            headers={"X-API-Key": api_key} if api_key else None,
            timeout=30,
        )
        resp.raise_for_status()
        data = resp.json()
        text = data.get("text") or ""
        # Pass text to ingestion pipeline
        start_ingestion_from_text(text, source_url=url, ingestion_id=ingestion_id)
    except Exception as e:
        # Handle fetch errors
        logger.error(f"Error fetching {url}: {e}")
```

Handle errors gracefully and ensure that network failures do not crash the service.

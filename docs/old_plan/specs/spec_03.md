# Spec 03 – Implement a file upload endpoint

This specification describes the REST API endpoint used to upload documents for ingestion.

## Endpoint Definition

Define a `POST /upload/file` endpoint in your FastAPI application that accepts multipart/form‑data uploads of PDF, Word and Markdown files.

```python
from fastapi import FastAPI, UploadFile, File, HTTPException, BackgroundTasks
import shutil
import uuid

app = FastAPI()

@app.post("/upload/file")
async def upload_file(file: UploadFile = File(...), background_tasks: BackgroundTasks = None):
    # Validate file type
    if file.content_type not in {"application/pdf", "application/vnd.openxmlformats-officedocument.wordprocessingml.document", "text/markdown"}:
        raise HTTPException(status_code=400, detail="Unsupported file type")

    # Save to temporary location
    tmp_filename = f"{uuid.uuid4()}_{file.filename}"
    tmp_path = f"/tmp/{tmp_filename}"
    with open(tmp_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    # Enqueue ingestion asynchronously (pseudo‑code)
    if background_tasks:
        background_tasks.add_task(start_ingestion, tmp_path, file.filename)
    else:
        start_ingestion(tmp_path, file.filename)

    return {"status": "accepted", "ingestion_id": tmp_filename}

```

`start_ingestion` should be defined in the ingestion module to parse, chunk, embed and persist the document.  Consider using background tasks to avoid blocking the request.  Return a unique `ingestion_id` so the client can query status if needed.

## Error Handling

If the file type is unsupported, respond with a 400 error.  Catch other exceptions (e.g., file I/O errors) and return a 500 error with a generic message.  Log detailed errors for debugging.

## Security Considerations

Validate and sanitize file names to prevent directory traversal attacks.  Limit maximum file size via FastAPI configuration.  In production, store uploaded files in a secure location rather than `/tmp`.

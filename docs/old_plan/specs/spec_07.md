# Spec 07 – Persist original artifacts

This specification describes how to store uploaded files and downloaded web pages so that they can be retrieved later.

## Storage Location

Create a directory tree `artifacts/` with subdirectories for different resource types:

```
artifacts/
├── uploads/        # original uploaded documents
├── web/            # downloaded web pages (HTML and extracted text)
└── answers/        # generated Markdown files for download
```

Each saved artifact should have a unique identifier (e.g., a UUID) and a metadata file describing the resource:

```
artifacts/uploads/{artifact_id}.pdf
artifacts/uploads/{artifact_id}.meta.json
```

Example metadata structure:

```json
{
  "filename": "user_manual.pdf",
  "upload_time": "2025-10-31T12:00:00Z",
  "mime_type": "application/pdf",
  "source": "upload",
  "vector_ids": ["123", "124", "125"]
}
```

## Implementation

Write helper functions to save files and metadata:

```python
import uuid
import json
import os

ARTIFACT_DIR = "artifacts/uploads"
os.makedirs(ARTIFACT_DIR, exist_ok=True)

def save_upload(file_path: str, original_name: str, vector_ids: list[str]) -> str:
    artifact_id = str(uuid.uuid4())
    # Copy file to artifacts directory
    new_path = os.path.join(ARTIFACT_DIR, f"{artifact_id}_{original_name}")
    os.rename(file_path, new_path)
    # Write metadata
    meta = {
        "filename": original_name,
        "upload_time": datetime.utcnow().isoformat() + "Z",
        "mime_type": mimetypes.guess_type(original_name)[0],
        "source": "upload",
        "vector_ids": vector_ids,
    }
    with open(os.path.join(ARTIFACT_DIR, f"{artifact_id}.meta.json"), "w") as f:
        json.dump(meta, f)
    return artifact_id
```

Repeat analogous functions for downloaded web pages and generated answers.  When deployed, replace the local directory with a cloud storage bucket (e.g., Firebase Storage, AWS S3) and adjust file I/O accordingly.

## Download Endpoint

Expose an endpoint (see Task 24) to download raw artifacts or generated answers by ID.  The endpoint should look up the file by artifact ID, read the metadata to determine content type and return the file with appropriate headers.

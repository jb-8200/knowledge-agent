# Spec 24 – Implement download as Markdown

Users can download the final answer and its citations as a Markdown file.  This specification describes the backend implementation.

## Backend Endpoint

Create a `GET /download/{answer_id}` endpoint that retrieves the answer from the session memory or artifact store, converts it to Markdown and returns it as a file response:

```python
from fastapi import FastAPI, HTTPException, Response
import io

app = FastAPI()

@app.get("/download/{answer_id}")
async def download_answer(answer_id: str, session_id: str = Depends(get_session_id)):
    session = get_session(session_id)
    answer = retrieve_answer(answer_id)
    if not answer:
        raise HTTPException(status_code=404, detail="Answer not found")
    citations = retrieve_citations(answer_id)
    # Format markdown
    md_content = f"## Answer\n\n{answer}\n\n### Citations\n"
    for idx, cite in enumerate(citations, start=1):
        md_content += f"[{idx}] {cite}\n"
    # Return as file
    headers = {
        "Content-Disposition": f"attachment; filename={answer_id}.md",
        "Content-Type": "text/markdown; charset=utf-8",
    }
    return Response(content=md_content, headers=headers)
```

`retrieve_answer` and `retrieve_citations` should access the session memory or artifact store where answers and citations are stored.  The endpoint sets the `Content-Disposition` header to prompt the browser to download the file.

## Client Implementation

Add a “Download as MD” button in the UI.  When clicked, call the `/download/{answer_id}` endpoint using `fetch` and programmatically trigger the file download (see Spec 19).  Enable the button only after a result is available.

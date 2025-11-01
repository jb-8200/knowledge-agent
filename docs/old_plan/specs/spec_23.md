# Spec 23 – Implement pinning of answers

Pinning allows users to save important answers as brief notes displayed on the side of the page.

## Backend Endpoint

Define a `POST /pin` endpoint that accepts an answer ID and an optional summary:

```python
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

app = FastAPI()

class PinRequest(BaseModel):
    answer_id: str
    snippet: str = ""

@app.post("/pin")
async def pin_answer(req: PinRequest, session_id: str = Depends(get_session_id)):
    session = get_session(session_id)
    # Retrieve the answer from memory or artifact store
    answer_text = retrieve_answer(req.answer_id)
    if not answer_text:
        raise HTTPException(status_code=404, detail="Answer not found")
    # Use provided snippet or truncate the answer
    snippet = req.snippet or answer_text[:200]
    pinned = {
        "answer_id": req.answer_id,
        "snippet": snippet,
        "timestamp": datetime.utcnow().isoformat() + "Z",
    }
    session.setdefault("pinned", []).append(pinned)
    return {"status": "pinned", "pinned": session["pinned"]}
```

## Unpinning

Allow users to remove a pinned note via a `DELETE /pin/{answer_id}` endpoint.  Filter the pinned list in the session store to remove the entry.

## UI Integration

On the client side, provide a pin icon next to each answer.  When clicked, call the `/pin` endpoint.  Display pinned notes in the sidebar by iterating over the `pinned` array in the server’s response.  Provide an unpin icon next to each pinned note.

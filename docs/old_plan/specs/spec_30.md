# Spec 30 – Implement feedback capture and evaluation

Capturing user feedback and evaluating system performance is key to continuous improvement.

## Feedback Endpoint

Define a `POST /feedback` endpoint that accepts a rating and optional comment:

```python
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field

app = FastAPI()

class FeedbackRequest(BaseModel):
    answer_id: str
    rating: int = Field(..., ge=1, le=5)
    comment: str = ""

feedback_storage: list[dict] = []

@app.post("/feedback")
async def submit_feedback(req: FeedbackRequest, session_id: str = Depends(get_session_id)):
    # Validate that the answer exists
    if not retrieve_answer(req.answer_id):
        raise HTTPException(status_code=404, detail="Answer not found")
    feedback = {
        "answer_id": req.answer_id,
        "session_id": session_id,
        "rating": req.rating,
        "comment": req.comment,
        "timestamp": datetime.utcnow().isoformat() + "Z",
    }
    feedback_storage.append(feedback)
    return {"status": "recorded"}
```

In production, store feedback in a database (e.g., Postgres, Firestore) rather than an in‑memory list.

## Feedback Analysis

Create a script or scheduled job that reads collected feedback and computes metrics such as average rating per answer, rating distribution, and common issues mentioned in comments.  Use these insights to adjust prompts, retrieval parameters and summarization strategies.

Optionally, integrate a RAG evaluation framework (e.g., [RAGAS](https://github.com/explodinggradients/ragas)) to automatically evaluate answer quality using reference answers.  Combine automated scores with user feedback to guide improvements.

## Testing

Write tests to verify that feedback submissions are stored correctly and that invalid ratings or answer IDs result in appropriate errors.  Mock the evaluation pipeline if integrating external libraries.

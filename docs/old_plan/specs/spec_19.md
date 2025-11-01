# Spec 19 – Implement client‑side API integration

This specification describes how the front‑end sends queries, feedback and other requests to the backend.

## Fetch Wrapper

Create a helper function to perform POST requests and handle JSON responses:

```javascript
async function postJson(url, data) {
  try {
    const response = await fetch(url, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify(data)
    });
    if (!response.ok) {
      throw new Error(`HTTP ${response.status}`);
    }
    return await response.json();
  } catch (error) {
    console.error('Request failed:', error);
    throw error;
  }
}
```

## Sending a Query

```javascript
async function submitQuery() {
  const queryInput = document.getElementById('query');
  const query = queryInput.value.trim();
  if (!query) return;
  // Optional: include session ID if stored in localStorage
  const sessionId = localStorage.getItem('session_id');
  const data = { query, session_id: sessionId };
  const result = await postJson('/query', data);
  renderAnswer(result);
}

document.getElementById('search-form').addEventListener('submit', async (e) => {
  e.preventDefault();
  await submitQuery();
});
```

## Feedback, Pin and Download

```javascript
async function sendFeedback(answerId, rating, comment) {
  await postJson('/feedback', { answer_id: answerId, rating, comment });
}

async function pinAnswer(answerId, snippet) {
  await postJson('/pin', { answer_id: answerId, snippet });
}

async function downloadMarkdown(answerId) {
  const response = await fetch(`/download/${answerId}`);
  const blob = await response.blob();
  const url = URL.createObjectURL(blob);
  const a = document.createElement('a');
  a.href = url;
  a.download = `${answerId}.md`;
  a.click();
  URL.revokeObjectURL(url);
}
```

## Error Handling and UI Updates

Wrap API calls in `try/catch` blocks to handle network errors.  Show a user‑friendly message when an error occurs.  Disable the download button until a result is available.  After successfully pinning or unpinning an answer, refresh the pinned notes section.

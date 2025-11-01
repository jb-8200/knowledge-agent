# Spec 20 – Render dynamic content

This specification details how to populate the UI with data returned from the backend.

## Rendering the Answer

Define a function `renderAnswer(data)` that receives the backend response and updates the DOM:

```javascript
function renderAnswer(data) {
  // Enable download button
  const downloadBtn = document.getElementById('download-md');
  downloadBtn.disabled = false;
  downloadBtn.onclick = () => downloadMarkdown(data.answer_id);

  // Answer text
  document.getElementById('answer').textContent = data.answer;

  // Citations list
  const citationsEl = document.getElementById('citations');
  citationsEl.innerHTML = '';
  data.citations.forEach((cite, idx) => {
    const anchor = document.createElement('a');
    anchor.href = cite.url || '#';
    anchor.textContent = `[${idx + 1}]`;
    anchor.target = '_blank';
    citationsEl.appendChild(anchor);
  });

  // Internal document links
  const internalList = document.getElementById('internal-links');
  internalList.innerHTML = '';
  data.internal_links.forEach((doc) => {
    const li = document.createElement('li');
    li.textContent = doc.metadata.filename || `Doc ${doc.metadata.doc_id}`;
    li.onclick = () => alert(`Open document ${doc.metadata.doc_id}`);
    internalList.appendChild(li);
  });

  // External links
  const externalList = document.getElementById('external-links');
  externalList.innerHTML = '';
  data.external_links.forEach((url) => {
    const li = document.createElement('li');
    const a = document.createElement('a');
    a.href = url;
    a.textContent = url;
    a.target = '_blank';
    li.appendChild(a);
    externalList.appendChild(li);
  });

  // YouTube thumbnails
  const ytContainer = document.getElementById('youtube-thumbnails');
  ytContainer.innerHTML = '';
  data.youtube_thumbnails?.forEach((thumb) => {
    const img = document.createElement('img');
    img.src = thumb.thumbnail_url;
    img.alt = thumb.title;
    img.onclick = () => window.open(thumb.url, '_blank');
    ytContainer.appendChild(img);
  });

  // Related questions
  const qList = document.getElementById('related-questions');
  qList.innerHTML = '';
  data.related_questions?.forEach((q) => {
    const li = document.createElement('li');
    li.textContent = q;
    li.onclick = () => {
      document.getElementById('query').value = q;
      submitQuery();
    };
    qList.appendChild(li);
  });

  // Pinned notes
  const pinnedList = document.getElementById('pinned-list');
  pinnedList.innerHTML = '';
  data.pinned?.forEach((note) => {
    const li = document.createElement('li');
    li.textContent = note.snippet;
    pinnedList.appendChild(li);
  });
}
```

## Handling Loading States

Before sending a query, clear previous content and show a loading indicator (e.g., spinner).  Hide the spinner once the response is processed.  Disable the search button during the request to prevent duplicate submissions.

## Updating Pinned Notes

When a user clicks the pin button next to an answer, call the `/pin` endpoint and refresh the pinned list using the updated session data returned by the backend.  Provide an option to unpin a note via the UI.

# Design: Web UI

## Objective

Create a simple, intuitive web interface for searching the knowledge base, modeled after Google Search with white theme and clear information hierarchy.

## Technical Design

### UI Layout

```
┌─────────────────────────────────────────────────┐
│  Knowledge Agent                    [User Menu] │
├─────────────────────────────────────────────────┤
│                                                 │
│          ┌─────────────────────┐                │
│          │  Search Box         │  [Search]      │
│          └─────────────────────┘                │
│                                                 │
├─────────────────────────────────┬───────────────┤
│  Answer Section                 │  Pinned Notes │
│  ┌───────────────────────────┐  │  ┌─────────┐ │
│  │ Synthesized Answer [1][2] │  │  │ Note 1  │ │
│  │ ...with citations         │  │  │ Note 2  │ │
│  └───────────────────────────┘  │  └─────────┘ │
│                                 │               │
│  Citations                      │               │
│  [1] Document A (internal)      │               │
│  [E1] Website B (external)      │               │
│                                 │               │
│  Related Documents              │               │
│  • Doc 1 • Doc 2 • Doc 3        │               │
│                                 │               │
│  YouTube Videos                 │               │
│  [thumb] [thumb] [thumb]        │               │
│                                 │               │
│  Similar Questions              │               │
│  • Question 1                   │               │
│  • Question 2                   │               │
└─────────────────────────────────┴───────────────┘
```

## Key Changes

### 3.1 Frontend Structure

```
frontend/
├── index.html          # Main page
├── css/
│   ├── main.css       # White theme, Google-like
│   └── responsive.css # Mobile breakpoints
├── js/
│   ├── api.js         # API client
│   ├── search.js      # Search handling
│   ├── render.js      # Dynamic content rendering
│   └── pins.js        # Pin management
└── assets/
    └── icons/         # UI icons
```

### 3.2 API Integration

```javascript
// POST /api/query
const response = await fetch('/api/query', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({
    query: userQuery,
    session_id: sessionId
  })
});

// Response structure
{
  "answer": "Synthesized answer text [1][2]",
  "citations": {
    "internal": [
      {"id": 1, "title": "Doc A", "url": "/doc/123"}
    ],
    "external": [
      {"id": "E1", "title": "Site B", "url": "https://..."}
    ]
  },
  "related_docs": [...],
  "youtube_thumbnails": [...],
  "similar_questions": [...]
}
```

### 3.3 Component Responsibilities

**index.html**: Page structure, semantic HTML
**main.css**: White theme styling, typography
**api.js**: Fetch abstraction, error handling
**search.js**: Form handling, query submission
**render.js**: Dynamic content insertion, citation formatting
**pins.js**: LocalStorage-based pin management

## Technology Stack

- **HTML5**: Semantic markup
- **CSS3**: Grid/Flexbox for layout
- **Vanilla JavaScript**: No framework (keep it simple)
- **LocalStorage**: Pin persistence
- **Fetch API**: Backend communication

## Alternatives Considered

1. **Framework**: React vs. Vue vs. Vanilla JS
   - Chose Vanilla: Simpler, no build step, faster load
2. **Styling**: Tailwind vs. Custom CSS
   - Chose Custom: Better control, smaller bundle
3. **State Management**: Redux vs. LocalStorage
   - Chose LocalStorage: Sufficient for pins/session

## Out of Scope

- User authentication UI
- Document upload interface
- Admin panel
- Dark mode (can add later)

# Design: Pin Answers

## Objective
Allow users to pin answers for quick reference, persisted in session.

## Technical Design

### Frontend
- Pin icon next to each answer
- Sidebar displays pinned notes
- LocalStorage for persistence

### Backend
- POST /api/pins - Add pin
- DELETE /api/pins/{id} - Remove pin
- GET /api/pins - List all pins

### Data Model
```python
class Pin(BaseModel):
    id: str
    query: str
    answer: str
    created_at: datetime
```

## Out of Scope
- Cross-session pin sharing
- Pin organization/folders
- Pin search

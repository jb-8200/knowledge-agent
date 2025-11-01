# Design: Deployment

## Objective
Deploy frontend to Firebase Hosting and backend to Cloud Run/ECS.

## Architecture
- **Frontend**: Firebase Hosting (static HTML/CSS/JS)
- **Backend**: Cloud Run (containerized FastAPI) or AWS ECS
- **Qdrant**: Managed Qdrant Cloud or self-hosted

## Configuration Files

### firebase.json
```json
{
  "hosting": {
    "public": "frontend",
    "rewrites": [{
      "source": "/api/**",
      "function": "api"
    }]
  }
}
```

### Dockerfile
```dockerfile
FROM python:3.10-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY app/ ./app/
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8080"]
```

## Out of Scope
- Auto-scaling configuration
- CDN setup
- SSL certificates (handled by platform)

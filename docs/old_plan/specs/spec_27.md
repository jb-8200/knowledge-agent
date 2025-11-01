# Spec 27 – Set up CORS and placeholders for authentication

This specification explains how to enable Cross‑Origin Resource Sharing (CORS) and prepare for future authentication.

## CORS Configuration

Use FastAPI’s `CORSMiddleware` to allow requests from the front‑end domain (e.g., your Firebase Hosting URL):

```python
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

origins = [
    "https://your-project.web.app",  # Replace with your Firebase hosting URL
    "http://localhost:5000",        # Development server
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

Adjust the `origins` list to match your deployment domains.  For local development, include `http://localhost:<port>`.

## Authentication Placeholders

Add placeholder functions or middleware for validating user tokens.  For example, if you plan to use Firebase Authentication later:

```python
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

bearer_scheme = HTTPBearer(auto_error=False)

async def get_current_user(token: HTTPAuthorizationCredentials = Depends(bearer_scheme)):
    if not token:
        return None  # unauthenticated
    # TODO: validate token using Firebase Admin SDK or other provider
    # If invalid, raise HTTPException
    return {"uid": "anonymous"}

@app.get("/protected-endpoint")
async def protected_endpoint(user = Depends(get_current_user)):
    if user is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Authentication required")
    return {"message": "Hello", "user": user}
```

Do not enforce authentication on the prototype’s core endpoints, but leave these stubs so that auth can be added without modifying the handler logic.

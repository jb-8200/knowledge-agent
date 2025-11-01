"""Knowledge Base Agent - FastAPI Application.

Main application entry point for the document ingestion and Q&A system.
"""

from fastapi import FastAPI
from app.routes import upload

app = FastAPI(
    title="Knowledge Base Agent",
    description="Document ingestion and Q&A system using RAG + CAG",
    version="0.1.0",
)

# Include routers
app.include_router(upload.router, prefix="/upload", tags=["ingestion"])


@app.get("/")
async def root():
    """Root endpoint providing API information."""
    return {
        "message": "Knowledge Base Agent API",
        "version": "0.1.0",
        "docs": "/docs",
    }


@app.get("/health")
async def health():
    """Health check endpoint."""
    return {"status": "healthy"}

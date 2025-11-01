# Spec 02 – Create a `.env` file with configuration placeholders

The application reads configuration from a `.env` file using `python-dotenv`.  This file should not be committed to version control.

## `.env` File Contents

Create a file named `.env` in the project root with the following key–value pairs:

```dotenv
# API key for your chosen LLM provider (e.g., OpenAI, Anthropic, Cohere).  Leave blank if using a local model.
MODEL_PROVIDER_API_KEY=

# URL for the Qdrant instance (default port is 6333)
QDRANT_URL=http://localhost:6333

# API key for the web search provider (e.g., Tavily, Serper) used in external search
SEARCH_API_KEY=

# API key for the YouTube Data API
YOUTUBE_API_KEY=

# API key for Firecrawl (optional – many endpoints are public)
FIRECRAWL_API_KEY=

# Placeholder for future authentication tokens (e.g., Firebase Auth)
AUTH_TOKEN_PLACEHOLDER=
```

## Loading Environment Variables

In your Python application, load these variables at startup using `python‑dotenv`:

```python
from dotenv import load_dotenv
import os

load_dotenv()

MODEL_API_KEY = os.environ.get("MODEL_PROVIDER_API_KEY")
QDRANT_URL = os.environ.get("QDRANT_URL", "http://localhost:6333")
SEARCH_API_KEY = os.environ.get("SEARCH_API_KEY")
YOUTUBE_API_KEY = os.environ.get("YOUTUBE_API_KEY")
FIRECRAWL_API_KEY = os.environ.get("FIRECRAWL_API_KEY")

# Placeholder usage for future authentication
AUTH_TOKEN = os.environ.get("AUTH_TOKEN_PLACEHOLDER")
```

Ensure that the `.env` file is listed in `.gitignore` so that secrets are not checked into version control.

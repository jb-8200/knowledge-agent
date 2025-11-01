# Spec 11 – Prepare external search configuration

Integrating external search requires proper configuration of the chosen provider.  This specification outlines the configuration process.

## Environment Variables

Store the API key for the search provider in the `.env` file under `SEARCH_API_KEY` (see Spec 02).  Additional environment variables may include:

* `SEARCH_PROVIDER` – a string indicating which provider to use (`tavily`, `serper`, etc.).
* `MAX_SEARCH_RESULTS` – the maximum number of results to retrieve.

## Configuration Module

Create a configuration module to load and validate search settings:

```python
import os
from pydantic import BaseModel, ValidationError

class SearchConfig(BaseModel):
    provider: str
    api_key: str
    max_results: int = 5

def load_search_config() -> SearchConfig:
    try:
        return SearchConfig(
            provider=os.environ.get("SEARCH_PROVIDER", "tavily"),
            api_key=os.environ["SEARCH_API_KEY"],
            max_results=int(os.environ.get("MAX_SEARCH_RESULTS", 5)),
        )
    except KeyError as e:
        raise RuntimeError(f"Missing search configuration: {e}")

search_config = load_search_config()
```

This module raises an error if required variables are missing.  The rest of the application should import `search_config` when instantiating search tools.

## Switching Providers

By abstracting configuration, you can switch search providers by changing the environment variables without modifying code.  If you plan to support multiple providers simultaneously, implement a factory pattern that returns the appropriate search client based on the `provider` field.

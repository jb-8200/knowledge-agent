# Spec 08 – Implement vector search logic

This specification covers how to perform similarity search over the Qdrant vector store.

## Query Embedding

To search for relevant passages, embed the user’s query using the same embedding model used for documents (from Spec 06):

```python
def embed_query(query: str) -> list[float]:
    return model.encode([query], show_progress_bar=False)[0].tolist()
```

If using LangChain embeddings:

```python
query_vector = embeddings.embed_query(query)
```

## Qdrant Search

Use the Qdrant client’s `search` method to retrieve the nearest neighbours:

```python
from qdrant_client import QdrantClient
from qdrant_client.http.models import SearchRequest

def search_vectors(query: str, top_k: int = 5) -> list[dict]:
    query_vector = embed_query(query)
    result = client.search(
        collection_name=COLLECTION_NAME,
        query_vector=query_vector,
        limit=top_k,
        with_payload=True,
    )
    passages = []
    for hit in result:
        passages.append({
            "text": hit.payload.get("text"),
            "metadata": hit.payload.get("metadata", {}),
            "score": hit.score,
        })
    return passages
```

The `with_payload=True` flag ensures that the document text and metadata are returned.  The metadata should include identifiers for citation.  Consider adding filters to restrict search by document type or user session if needed.

## Edge Cases

* When the query is empty or shorter than a threshold, return an empty list or a default response.
* If the vector store is empty, return an informative message indicating that no documents have been uploaded.

## Test Scenarios

* Search for a term present in a known document and verify that the top passage corresponds to the correct document.
* Search for a term not present in any document and verify that the result list is empty.
* Validate that the similarity scores decrease as results become less relevant.

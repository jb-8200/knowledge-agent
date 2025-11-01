# Spec 06 – Generate vector embeddings

This specification describes the process for generating vector representations of text chunks and storing them in a Qdrant vector database.

## Embedding Model

Use an open‑source model from the `sentence-transformers` library (e.g., `all-MiniLM-L6-v2`) to convert chunks into fixed‑dimensional vectors:

```python
from sentence_transformers import SentenceTransformer
model = SentenceTransformer("all-MiniLM-L6-v2")

def embed_texts(texts: list[str]) -> list[list[float]]:
    return model.encode(texts, show_progress_bar=False).tolist()
```

Alternatively, use LangChain’s embedding wrappers for compatibility with different LLM providers:

```python
from langchain.embeddings import HuggingFaceEmbeddings
embeddings = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")
vectors = embeddings.embed_documents(texts)
```

## Qdrant Integration

Use the `qdrant-client` library to create a collection and upload vectors:

```python
from qdrant_client import QdrantClient, models
import os

client = QdrantClient(url=os.environ.get("QDRANT_URL", "http://localhost:6333"))

COLLECTION_NAME = "kb_passages"
DIMENSION = 384  # embedding dimension for MiniLM models

# Create collection if it does not exist
if COLLECTION_NAME not in client.get_collections().collections:
    client.create_collection(
        collection_name=COLLECTION_NAME,
        vectors_config=models.VectorParams(size=DIMENSION, distance=models.Distance.COSINE),
    )

def upload_embeddings(vectors: list[list[float]], payloads: list[dict]):
    ids = [str(i) for i in range(len(vectors))]
    client.upsert(
        collection_name=COLLECTION_NAME,
        points=models.Batch(ids=ids, vectors=vectors, payloads=payloads),
    )
```

The `payloads` list should contain metadata for each chunk, including document ID, chunk index and original filename.  Ensure that vector and payload arrays are aligned by index.

## Considerations

* Batch uploads in chunks to avoid overwhelming memory (e.g., batch size of 100).
* Choose an appropriate distance metric (cosine similarity is common for sentence embeddings).
* For large corpora, consider enabling persistence and replicating the Qdrant container for fault tolerance.

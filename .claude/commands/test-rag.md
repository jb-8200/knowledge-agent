Quickly test the RAG (Retrieval-Augmented Generation) pipeline end-to-end.

## Usage

```
/test-rag "What is machine learning?"
```

Or without arguments to test with default query:

```
/test-rag
```

## What This Does

1. **Tests vector search**: Queries Qdrant for relevant chunks
2. **Checks retrieval quality**: Verifies results have good similarity scores
3. **Tests context assembly**: Shows how chunks would be assembled for LLM
4. **Validates metadata**: Ensures source attribution is present
5. **Performance metrics**: Shows query latency and result counts

## Steps

### 1. Validate Prerequisites

Check that required services are running:

```bash
# Check if Qdrant is accessible
curl -s http://localhost:6333/health || echo "⚠️  Qdrant not running"

# Check if collection exists
curl -s http://localhost:6333/collections/kb_passages || echo "⚠️  Collection not found"

# Check if there are any vectors
python -c "from ingestion.vector_store import get_vector_store; vs = get_vector_store(); print(f'Vectors in store: {vs.client.count(collection_name=\"kb_passages\").count}')"
```

### 2. Determine Query

Use provided query argument or default test query:

```python
DEFAULT_QUERY = "How do I upload documents to the knowledge base?"
query = args.get("query", DEFAULT_QUERY)
```

### 3. Execute Vector Search

```python
from ingestion.vector_store import get_vector_store
import time

vs = get_vector_store()

start = time.time()
results = vs.search(query=query, limit=5, score_threshold=0.5)
latency = time.time() - start
```

### 4. Display Results

Show formatted results with context:

```python
for i, result in enumerate(results, 1):
    print(f"\n{i}. Score: {result['score']:.3f}")
    print(f"   Source: {result['metadata']['filename']}")
    print(f"   Text: {result['text'][:200]}...")
    print(f"   Metadata: {result['metadata']}")
```

### 5. Assemble RAG Context

Show how chunks would be formatted for LLM prompt:

```python
context = "\n\n".join([
    f"[Source: {r['metadata']['filename']}]\n{r['text']}"
    for r in results
])

print(f"\n📝 RAG Context (for LLM):\n{context}")
```

### 6. Performance Metrics

Report query performance:

```python
print(f"\n⏱️  Query latency: {latency*1000:.1f}ms")
print(f"📊 Results returned: {len(results)}")
print(f"🎯 Average score: {sum(r['score'] for r in results)/len(results):.3f}")
```

## Output Format

### Successful Test

```
🔍 Testing RAG Pipeline
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Query: "What is machine learning?"

✅ Prerequisites:
✅ Qdrant running (http://localhost:6333)
✅ Collection exists (kb_passages)
✅ Vectors indexed: 342 chunks

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

📊 Search Results:

1. Score: 0.847
   Source: ml-introduction.pdf (chunk 3/12)
   Text: Machine learning is a subset of artificial intelligence that enables systems to learn and improve from experience without being explicitly programmed. It focuses on developing algorithms...

2. Score: 0.823
   Source: ai-fundamentals.docx (chunk 7/15)
   Text: Supervised learning algorithms are trained on labeled data, where the correct output is known. The algorithm learns to map inputs to outputs by finding patterns in the training data...

3. Score: 0.791
   Source: https://example.com/ml-guide (chunk 2/8)
   Text: The three main types of machine learning are supervised learning, unsupervised learning, and reinforcement learning. Each approach has different use cases and requirements...

4. Score: 0.765
   Source: ml-introduction.pdf (chunk 4/12)
   Text: Common machine learning applications include image recognition, natural language processing, recommendation systems, fraud detection, and predictive analytics...

5. Score: 0.742
   Source: deep-learning.md (chunk 1/6)
   Text: Deep learning is a specialized subset of machine learning that uses neural networks with multiple layers. These networks can automatically learn hierarchical representations...

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

📝 Assembled RAG Context (for LLM):

[Source: ml-introduction.pdf]
Machine learning is a subset of artificial intelligence that enables systems to learn and improve from experience without being explicitly programmed. It focuses on developing algorithms...

[Source: ai-fundamentals.docx]
Supervised learning algorithms are trained on labeled data, where the correct output is known. The algorithm learns to map inputs to outputs by finding patterns in the training data...

[Source: https://example.com/ml-guide]
The three main types of machine learning are supervised learning, unsupervised learning, and reinforcement learning. Each approach has different use cases and requirements...

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

⏱️  Performance Metrics:

Query latency: 45.2ms
Results returned: 5/5
Average similarity: 0.794
Min score: 0.742
Max score: 0.847

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

✅ RAG Pipeline Test: PASSED

Quality indicators:
✅ Latency < 100ms
✅ Average score > 0.7
✅ All results above threshold
✅ Diverse sources (3 different documents)
✅ Metadata complete

Pipeline ready for production use.
```

### No Results Found

```
🔍 Testing RAG Pipeline
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Query: "quantum computing basics"

✅ Prerequisites:
✅ Qdrant running
✅ Collection exists
✅ Vectors indexed: 342 chunks

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

⚠️  No results found above threshold (0.5)

This could mean:
1. No indexed content about "quantum computing basics"
2. Query phrasing doesn't match indexed content
3. Threshold (0.5) is too high

Suggestions:
- Lower threshold: vs.search(query, score_threshold=0.3)
- Rephrase query to match document language
- Ingest more relevant documents

Try a different query or ingest documents on this topic.
```

### Service Down

```
🔍 Testing RAG Pipeline
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

❌ Prerequisites Failed:

❌ Qdrant not running
   Start with: docker run -p 6333:6333 qdrant/qdrant

Cannot test RAG pipeline without Qdrant.
```

### Empty Collection

```
🔍 Testing RAG Pipeline
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

✅ Qdrant running
⚠️  Collection empty (0 vectors)

Ingest some documents first:
- /ingest tests/fixtures/sample.pdf
- Or use: POST /upload/file
- Or use: POST /upload/link

Collection must have vectors before testing search.
```

## Advanced Usage

### Test with Score Threshold

```python
# In the command implementation:
threshold = args.get("threshold", 0.5)
results = vs.search(query=query, limit=5, score_threshold=threshold)
```

Usage:
```
/test-rag "machine learning" threshold:0.7
```

### Test with Custom Limit

```
/test-rag "machine learning" limit:10
```

### Test with Specific Collection

```
/test-rag "machine learning" collection:kb_passages_v2
```

## Debugging Tips

If results are poor:
1. **Check embedding model**: Ensure same model used for indexing and querying
2. **Inspect metadata**: Verify chunks have correct source information
3. **Test chunking**: Check if chunk sizes are appropriate (not too large/small)
4. **Review scores**: Scores < 0.6 indicate weak matches
5. **Try similar queries**: Rephrase to match document language

## Integration with LangChain

This command shows raw vector search results. For full RAG with LLM:

```python
from langchain.chains import RetrievalQA
from langchain_openai import ChatOpenAI

# (This would be in the actual answer synthesis feature)
llm = ChatOpenAI(model="gpt-4")
qa_chain = RetrievalQA.from_chain_type(
    llm=llm,
    retriever=vector_store.as_retriever(),
    return_source_documents=True
)

result = qa_chain({"query": query})
print(result["result"])  # LLM-generated answer
print(result["source_documents"])  # Retrieved chunks
```

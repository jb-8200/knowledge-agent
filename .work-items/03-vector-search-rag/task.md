# Task Breakdown: Vector Search and RAG Retrieval

## Overview

Implement RAG (Retrieval-Augmented Generation) retrieval capabilities with vector similarity search over Qdrant, LangChain tool integration for composable workflows, and session-based conversation memory. This feature enables natural language querying of the indexed knowledge base with contextual multi-turn conversations.

## Requirements Traceability

- Links to: `user-story.md` - Research Analyst needs searchable knowledge base with conversation context
- Links to: `design.md` - Technical architecture for vector search, tool integration, and memory
- Original tasks: Task 08 (vector search), Task 09 (LangChain tool), Task 10 (session memory)

## Test Strategy

- **Unit Tests**:
  - Query embedding with same model as documents
  - Vector search with various queries and top-K values
  - Edge cases: empty queries, empty database, invalid inputs
  - Tool wrapper invocation and output validation
  - Session CRUD operations (create, get, update, clear)
  - Memory isolation between sessions

- **Integration Tests**:
  - End-to-end query flow: embed → search → rank → return
  - Tool integration with LangChain chains
  - Multi-turn conversation with memory persistence
  - Session lifecycle: create → interact → clear
  - Qdrant connection error handling

- **Acceptance Tests**:
  - Search for known content and verify correct passage retrieval
  - Verify similarity scores and metadata completeness
  - Test follow-up questions use conversation history
  - Validate session isolation (no cross-contamination)
  - Confirm clear session removes all history

## Sequential Steps (TDD Approach)

Each step follows Red → Green → Refactor cycle:

### 01 - Implement Vector Search Logic

**Objective**: Create vector search service that embeds queries and retrieves top-K similar passages from Qdrant

**Acceptance Criteria**:
- Query embedding uses all-MiniLM-L6-v2 (same as document embeddings)
- Search returns top-K passages with text, metadata, and similarity scores
- Empty queries handled gracefully with validation error
- Metadata includes doc_id, filename, chunk_index, page_number, source
- Test: Known query retrieves expected passage as top result

**TDD Cycle**:
1. **Red**: Write tests expecting vector search to return ranked passages
2. **Green**: Implement query embedding, Qdrant search, result formatting
3. **Refactor**: Add filtering, error handling, logging, edge case validation

**Files Modified**:
- Create: `app/services/vector_search.py`
- Create: `tests/test_vector_search.py`
- Modify: `app/services/__init__.py`

**Estimated Time**: 3-4 hours

---

### 02 - Wrap Retrieval Logic as LangChain Tool

**Objective**: Expose vector search as composable LangChain Tool for chain/agent integration

**Acceptance Criteria**:
- Retrieval function defined with clear signature and type hints
- Function wrapped as LangChain StructuredTool with Pydantic schema
- Tool has descriptive name ("search_knowledge_base") and description
- Tool returns JSON-serializable dict with passages, query, count
- Test: Direct tool invocation and chain integration both work

**TDD Cycle**:
1. **Red**: Write tests expecting tool to be callable and return correct format
2. **Green**: Implement tool wrapper with StructuredTool and input schema
3. **Refactor**: Optimize output format, add documentation, improve error messages

**Files Modified**:
- Create: `app/tools/retriever.py`
- Create: `app/tools/__init__.py`
- Create: `tests/test_retriever_tool.py`

**Estimated Time**: 2-3 hours

---

### 03 - Configure Session and Memory Services

**Objective**: Implement session management with conversation history persistence

**Acceptance Criteria**:
- Session store maps session_id (UUID) to SessionMemory objects
- Memory stores conversation history (user/assistant messages)
- CRUD operations: get_or_create, add_interaction, clear_session
- LangChain ConversationBufferMemory integration for chain compatibility
- Test: Multi-turn conversation persists context, clear removes all history

**TDD Cycle**:
1. **Red**: Write tests expecting session operations and history persistence
2. **Green**: Implement in-memory session store with CRUD methods
3. **Refactor**: Add LangChain memory wrapper, session limits, timestamps

**Files Modified**:
- Create: `app/services/memory.py`
- Create: `app/routes/session.py` (API endpoints for session management)
- Create: `tests/test_memory_service.py`
- Create: `tests/test_session_api.py`
- Modify: `app/main.py` (include session router)

**Estimated Time**: 3-4 hours

---

## Commit Strategy

Following "Tidy First" methodology:

**Commit 1** (Step 01):
- Implement vector search service
- Add query embedding and Qdrant search
- Tests for search accuracy and edge cases

**Commit 2** (Step 02):
- Wrap search as LangChain StructuredTool
- Add Pydantic input schema and validation
- Tests for tool invocation and output format

**Commit 3** (Step 03):
- Implement session memory service
- Add conversation history persistence
- Add session API endpoints (GET, DELETE)
- Tests for multi-turn conversations and isolation

## Dependencies

- Feature F02: Document Ingestion (must be complete with documents in Qdrant)
- Qdrant running with `kb_passages` collection populated
- sentence-transformers model downloaded and accessible
- LangChain and LangGraph installed

## Blocks

- F04: RAG Q&A Agent depends on retrieval tool being available
- F05: Citation Generation depends on search results having metadata
- F06: Frontend query interface depends on /query endpoint

## Testing Prerequisites

Before starting, ensure:
1. Virtual environment activated with all dependencies
2. Qdrant running on localhost:6333 or configured URL
3. At least one document ingested (from F02) for search testing
4. sentence-transformers/all-MiniLM-L6-v2 model downloaded
5. Sample test queries prepared that match ingested content

## Post-Implementation Validation

After completing all steps:
1. Start FastAPI server: `uvicorn app.main:app --reload`
2. Test vector search directly in Python REPL
3. Invoke retrieval tool from LangChain chain
4. Create session, ask multiple questions, verify history
5. Clear session and verify memory is empty
6. Check logs for any errors or warnings
7. Run full test suite: `pytest tests/ -v`

## Performance Targets

- Query embedding: <100ms
- Vector search: <200ms (for 10k document chunks)
- Session operations: <10ms (in-memory)
- Total /query endpoint response: <500ms
- Memory per session: <10KB (100 interactions)

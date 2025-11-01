# Design: Answer Synthesis

## Objective

Implement a multi-stage answer generation system that combines Retrieval Augmented Generation (RAG) from internal documents with Contextual Answer Generation (CAG) from external sources. The system produces coherent, well-cited answers that integrate both internal knowledge and web-based information, with clear source attribution and conflict resolution.

## Technical Design

### System Architecture

The answer synthesis pipeline consists of four sequential stages:

1. **Synthesizer Chain** - Generate draft answer from internal passages with citations
2. **External Search** - Conditionally fetch and summarize web content when needed
3. **External Summarizer Chain** - Consolidate external sources into unified summary
4. **Critic Chain** - Merge internal and external content into final answer

### Data Flow

```
Query → Retrieval Tool → Internal Passages
                            ↓
                      Synthesizer Chain
                            ↓
                    {answer, needs_external, citations}
                            ↓
                   ┌────────┴────────┐
                   NO                YES
                   ↓                 ↓
              Skip External    External Search Tool
                   ↓                 ↓
                   │           Web Results
                   │                 ↓
                   │         External Summarizer
                   │                 ↓
                   │           {summary, citations}
                   │                 ↓
                   └────────┬────────┘
                            ↓
                      Critic Chain
                            ↓
                  {final_answer, ordered_citations}
                            ↓
                    Session Memory Update
                            ↓
                      Response Payload
```

## Key Components

### 3.1 Chain Architecture

**SynthesizerChain** (`chains/synthesizer.py`):
- Purpose: Draft answer using only internal passages
- Input: Query + list of passage dictionaries
- Output: `{answer: str, needs_external: bool, citations: list}`
- LLM: OpenAI or compatible (temperature=0 for determinism)
- Prompt strategy: Instruct to cite with brackets [1], [2] and signal "MORE_INFO_NEEDED"

**ExternalSummarizerChain** (`chains/external_summarizer.py`):
- Purpose: Consolidate multiple web page summaries
- Input: List of summary dictionaries from Firecrawl
- Output: `{summary: str, citations: list}`
- LLM: OpenAI or compatible (temperature=0)
- Prompt strategy: Preserve citations, avoid introducing new facts

**CriticChain** (`chains/critic.py`):
- Purpose: Merge internal and external content, resolve conflicts
- Input: Query + internal answer + external summary
- Output: `{answer: str, citations: list}`
- LLM: OpenAI or compatible (temperature=0)
- Prompt strategy: Prioritize internal sources, distinguish citation types [1] vs [E1]

**WorkflowOrchestrator** (`workflows/answer_workflow.py`):
- Purpose: Coordinate all chains and tools in correct order
- Input: Query + session context
- Output: Complete response payload
- Execution: Conditional logic or LangGraph state machine
- Memory: Update session history after completion

### 3.2 Prompt Templates

**Synthesizer Prompt**:
```python
from langchain.prompts import PromptTemplate

synth_prompt = PromptTemplate(
    input_variables=["question", "passages"],
    template=(
        "You are a helpful assistant answering questions using provided passages."
        " Answer the question based only on these passages."
        " Cite each passage you use with a bracketed number in the order of appearance (e.g., [1], [2])."
        " If the information is insufficient, reply 'MORE_INFO_NEEDED' at the end.\n\n"
        "Question: {question}\n\n"
        "Passages:\n{passages}\n\n"
        "Answer:"
    ),
)
```

**External Summarizer Prompt**:
```python
external_prompt = PromptTemplate(
    input_variables=["summaries"],
    template=(
        "You are aggregating information from external sources."
        " Combine the following summaries into a coherent set of factual statements."
        " For each fact, include the citation number corresponding to the source summary in brackets."
        " Do not introduce any information not present in the summaries.\n\n"
        "Summaries:\n{summaries}\n\n"
        "Combined Summary:"
    ),
)
```

**Critic Prompt**:
```python
critic_prompt = PromptTemplate(
    input_variables=["question", "internal_answer", "external_summary"],
    template=(
        "You are a critical reviewer combining two sources of information."
        " Given the question, an internal answer based on uploaded documents and an external summary from the web,"
        " craft a final answer that integrates both. Resolve any contradictions by preferring internal content unless the external source clearly corrects it."
        " Provide citations for each statement, numbering internal citations first (e.g., [1], [2]) and then external citations (e.g., [E1], [E2])."
        " If any information is uncertain or conflicted, mention it explicitly.\n\n"
        "Question: {question}\n\n"
        "Internal Answer:\n{internal_answer}\n\n"
        "External Summary:\n{external_summary}\n\n"
        "Final Answer:"
    ),
)
```

### 3.3 Data Models

**SynthesizerOutput**:
```python
from pydantic import BaseModel

class SynthesizerOutput(BaseModel):
    answer: str                    # Draft answer with [1], [2] citations
    needs_external: bool           # True if answer contains "MORE_INFO_NEEDED"
    citations: list[dict]          # Passage metadata from retrieval tool
```

**ExternalSummarizerOutput**:
```python
class ExternalSummarizerOutput(BaseModel):
    summary: str                   # Combined external information
    citations: list[dict]          # Web page URLs and metadata
```

**CriticOutput**:
```python
class CriticOutput(BaseModel):
    answer: str                    # Final synthesized answer
    citations: list[dict]          # Ordered: internal first, then external
```

**WorkflowResponse**:
```python
class WorkflowResponse(BaseModel):
    answer: str                             # Final answer from critic
    citations: list[dict]                   # All citations (internal + external)
    internal_links: list[dict]              # Passages from Qdrant
    external_links: list[dict]              # URLs from web search
    youtube_thumbnails: list[dict] | None   # Optional (from Task 21)
    similar_questions: list[str] | None     # Optional (from Task 22)
    pinned_notes: list[dict] | None         # From session memory
    session_id: str                         # For conversation tracking
```

### 3.4 Component Responsibilities

**run_synthesizer(question: str, passages: list[dict]) -> SynthesizerOutput**:
- Format passages as numbered list for prompt
- Invoke LLM chain with question and passages
- Parse response to detect "MORE_INFO_NEEDED" flag
- Remove flag from answer text
- Return structured output with citations

**run_external_summarizer(summaries: list[dict]) -> ExternalSummarizerOutput**:
- Format summaries with indices for citation tracking
- Invoke LLM chain to consolidate summaries
- Extract citation metadata (URLs, titles)
- Return combined summary with citations

**run_critic(question: str, internal: SynthesizerOutput, external: ExternalSummarizerOutput) -> CriticOutput**:
- Pass all inputs to LLM chain
- Combine citation lists (internal first, external second)
- Ensure citation numbering is consistent
- Return final answer with ordered citations

**handle_query(question: str, session_id: str) -> WorkflowResponse**:
- Load session context and history
- Call retrieval tool to get internal passages
- Run synthesizer chain
- Conditionally run external search and summarizer if `needs_external=True`
- Run critic chain to merge content
- Update session memory with Q&A
- Build complete response payload

### 3.5 External Services

**Retrieval Tool** (from F03):
- Input: Query string
- Output: `{passages: list[dict], metadata: dict}`
- Source: Qdrant vector search

**External Search Tool** (from F04):
- Input: Query string
- Output: `{results: list[dict], search_metadata: dict}`
- Source: Tavily API or similar

**Firecrawl Summarizer** (from Task 13):
- Input: URL
- Output: `{summary: str, url: str, title: str}`
- Source: Firecrawl API

**Session Memory**:
- Input: Session ID, question, answer, citations
- Output: Updated session state
- Storage: In-memory or Redis

## Technical Constraints

### LLM Configuration
- Temperature: 0 (deterministic output for testing)
- Model: OpenAI GPT-3.5-turbo or GPT-4 (configurable)
- Max tokens: 2000 for answers (prevent truncation)
- API key: From environment variable `MODEL_PROVIDER_API_KEY`

### Citation Format
- Internal: `[1]`, `[2]`, `[3]`, etc.
- External: `[E1]`, `[E2]`, `[E3]`, etc.
- Ordering: Internal citations always precede external citations

### Processing Time
- Synthesizer: ~2-5 seconds (single LLM call)
- External search + summarizer: ~10-15 seconds (network calls + LLM)
- Critic: ~2-5 seconds (single LLM call)
- Total workflow: 5-25 seconds depending on external search requirement

### Error Handling
- LLM API failures: Retry with exponential backoff (3 attempts)
- External search timeout: Proceed with internal-only answer
- Citation parsing errors: Log warning, continue with best-effort citations
- Session memory errors: Continue without memory update, log error

## Alternatives Considered

1. **Single-Stage Generation vs Multi-Stage**:
   - Chose: Multi-stage (Synthesizer → Critic)
   - Reason: Better separation of concerns, easier testing, clearer citations
   - Trade-off: More LLM calls, higher latency

2. **Magic String vs JSON Mode for `needs_external`**:
   - Chose: Magic string "MORE_INFO_NEEDED"
   - Reason: Simpler implementation, works with all LLM providers
   - Alternative: Use function calling or JSON mode if provider supports it

3. **Conditional Logic vs LangGraph**:
   - Chose: Start with conditional logic, migrate to LangGraph later
   - Reason: Simpler for MVP, LangGraph adds complexity
   - Migration path: Refactor to LangGraph state machine in future iteration

4. **Synchronous vs Asynchronous Workflow**:
   - Chose: Synchronous (blocking) for MVP
   - Reason: Simpler implementation, acceptable latency (<30s)
   - Future: Add async/await for concurrent external searches

5. **Citation Style**:
   - Considered: Footnotes, inline URLs, numbered brackets
   - Chose: Numbered brackets [1], [2] with separate citation list
   - Reason: Clean reading experience, easy to trace sources

## Out of Scope

- Real-time streaming of answer generation
- User-configurable citation styles
- Multi-turn conversation with context refinement
- Automatic fact-checking against multiple sources
- Confidence scores for individual claims
- Parallel evaluation of multiple answer strategies
- Custom LLM prompt templates (user-defined)
- Answer explanation or reasoning traces

## Dependencies

- Feature F02: Document Ingestion (provides internal passages)
- Feature F03: Vector Search RAG (retrieval tool)
- Feature F04: External Search (search tool and Firecrawl integration)
- Task 13: External page summarization (Firecrawl summaries)
- LangChain library (`langchain`, `langchain-openai`)
- OpenAI API key or compatible LLM provider

## Security Considerations

1. **LLM Prompt Injection**:
   - Risk: Malicious user queries manipulating LLM behavior
   - Mitigation: Validate input length, sanitize special characters, use system prompts

2. **Citation Manipulation**:
   - Risk: LLM generating fake citations or URLs
   - Mitigation: Validate all citations against actual retrieved passages/URLs

3. **API Key Security**:
   - Risk: Exposing LLM API keys in logs or responses
   - Mitigation: Load from environment, never log API keys, use key rotation

4. **Cost Control**:
   - Risk: Unbounded LLM API costs from excessive queries
   - Mitigation: Rate limiting per user, max token limits, caching

## Future Enhancements

- Implement LangGraph state machine for workflow visualization
- Add citation validation to detect hallucinated sources
- Support multiple LLM providers (Anthropic, Cohere, local models)
- Add confidence scoring for answer quality
- Implement caching for repeated queries
- Support multi-turn conversations with context management
- Add answer feedback loop (thumbs up/down) for improvement
- Generate answer explanations showing reasoning process

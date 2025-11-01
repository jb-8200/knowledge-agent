# Architecture Decision Records (ADRs)

This directory will contain Architecture Decision Records documenting significant architectural and technical decisions made during development.

## Format

Each ADR follows this naming convention:
```
NNNN-title-of-decision.md
```

Example: `0001-use-qdrant-for-vector-store.md`

## Template

When creating an ADR, use this template:

```markdown
# [Number]. [Title]

**Date**: YYYY-MM-DD
**Status**: [Proposed | Accepted | Deprecated | Superseded]
**Deciders**: [List of people involved]

## Context

What is the issue we're facing? What factors are in play?

## Decision

What decision are we making?

## Consequences

What becomes easier or more difficult because of this change?

### Positive
- Benefit 1
- Benefit 2

### Negative
- Tradeoff 1
- Tradeoff 2

## Alternatives Considered

What other options were considered?

1. **Alternative 1**
   - Pros: ...
   - Cons: ...
   - Why rejected: ...

2. **Alternative 2**
   - Pros: ...
   - Cons: ...
   - Why rejected: ...

## References

- Link to design docs
- Link to specifications
- External resources
```

## Existing Decisions

Some early decisions are documented in feature design documents:
- Vector store choice (Qdrant) → `.work-items/03-vector-search-rag/design.md`
- LLM framework (LangChain) → `.work-items/05-answer-synthesis/design.md`
- Web scraping (Firecrawl) → `.work-items/04-external-search/design.md`

Consider creating formal ADRs for these if needed.

## genai-specs Standards

For ADR standards and templates, see:
- `rules/standards-decision.mdc`
- `rules/standards-architecture.mdc`

## Usage

ADRs should be created when:
- Making significant architectural changes
- Choosing between major technical alternatives
- Establishing patterns that affect multiple features
- Making decisions with long-term consequences

---

**Status**: Ready for use
**First ADR**: To be created during development

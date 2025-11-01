# Design: Similar Questions

## Objective
Generate follow-up questions using LLM based on user's query and answer.

## Technical Design
Use simple LLM prompt to generate 5 related questions:

```python
prompt = f"""Based on this query: "{query}"
And this answer: "{answer}"

Generate 5 related questions someone might ask next.
Return only the questions, one per line."""

similar_questions = llm.invoke(prompt).split('\n')
```

## Out of Scope
- Question clustering
- Historical question tracking
- Personalization

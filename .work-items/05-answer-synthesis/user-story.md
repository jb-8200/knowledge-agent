# User Story: Answer Synthesis

## User Persona

**Name:** Research Analyst

**Description:** A knowledge worker who needs accurate, comprehensive answers from both internal knowledge bases and external sources. They require proper citations to verify information, trace claims back to source documents, and understand which information comes from trusted internal documents versus external web sources.

## Story

**As a** Research Analyst
**I want to** receive comprehensive answers with clear citations from both internal documents and external sources
**so that** I can verify information accuracy, understand the source of each claim, and make informed decisions based on traceable evidence

## Acceptance Criteria (EARS Format)

- WHEN I ask a question THEN I SHALL receive an answer synthesized from internal passages with bracketed citation numbers
- WHEN the internal knowledge is insufficient THEN I SHALL see the system automatically search external sources and integrate that information
- WHEN both internal and external sources are used THEN I SHALL see citations clearly distinguished (internal vs external)
- IF internal and external sources contradict THEN I SHALL see the system prioritize internal sources and note the discrepancy
- WHEN an answer includes citations THEN I SHALL be able to trace each statement back to its source document or URL
- WHEN external information is added THEN I SHALL see it clearly labeled with external citation markers (e.g., [E1], [E2])
- IF a question cannot be fully answered THEN I SHALL see the system acknowledge information gaps
- WHEN the answer is complete THEN I SHALL receive a final synthesized response that integrates all sources coherently
- WHEN citations are provided THEN I SHALL see them ordered with internal citations first, then external citations
- IF the system detects uncertain or conflicting information THEN I SHALL see those issues explicitly mentioned in the answer

## Success Metrics

- Answers include citations for all factual claims
- Internal passages are properly cited with bracketed numbers [1], [2], etc.
- External sources are cited with distinct markers [E1], [E2], etc.
- Synthesizer correctly signals when external information is needed
- External summarizer consolidates multiple web sources without introducing new information
- Critic chain successfully merges internal and external content
- Contradictions between sources are identified and resolved
- Final answers are coherent and well-structured with ordered citations
- Citation ordering is consistent (internal first, external second)
- Workflow correctly orchestrates all chains based on information needs

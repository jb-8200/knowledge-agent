Identify the current step in the active feature and guide you through the TDD cycle.

## Usage

```
/next-step
```

## What This Does

1. **Finds active feature**: Checks `.claude/plans/` for active symlinks
2. **Identifies current step**: Determines which numbered step you're on
3. **Shows TDD guide**: Displays Red → Green → Refactor cycle for the step
4. **Provides test examples**: Shows what tests to write (RED phase)
5. **Guides implementation**: Shows what to implement (GREEN phase)
6. **Suggests refactoring**: Shows quality improvements (REFACTOR phase)

## Steps

### 1. Find Active Feature

```bash
ls .claude/plans/*.plan.md
```

If multiple features are active, ask the user which one to work on.

### 2. Determine Current Step

Check git log and test files to identify which step is current:

```bash
# List all step files
ls .work-items/{feature-name}/*_*.md

# Check which tests exist
ls tests/test_*.py

# Check recent commits
git log --oneline -10
```

Logic:
- If step 01 tests don't exist → Current step is 01
- If step 01 tests pass but step 02 tests don't exist → Current step is 02
- If step N tests fail → Current step is N (in RED or GREEN phase)
- If step N tests pass → Current step is N (in REFACTOR phase or ready for N+1)

### 3. Read Current Step File

Read `.work-items/{feature-name}/{N}_*.md` to get:
- Objective
- Acceptance criteria
- TDD Red phase guidance
- TDD Green phase guidance
- TDD Refactor phase guidance

### 4. Determine TDD Phase

Run tests to determine phase:

```bash
pytest tests/test_{feature}.py -v --tb=short
```

- **No test file** → RED phase (need to write tests)
- **Tests exist but fail** → GREEN phase (need to implement code)
- **Tests pass** → REFACTOR phase (improve code quality)

### 5. Display Guidance

Based on the phase, show appropriate guidance:

#### RED Phase Output:
```
🔴 RED Phase: Write Failing Tests

Current Step: {N} - {step title}
Objective: {objective}

Write these tests in tests/test_{feature}.py:

{test code examples from step file}

Next: Run `pytest tests/test_{feature}.py -v` to verify tests fail
```

#### GREEN Phase Output:
```
🟢 GREEN Phase: Make Tests Pass

Current Step: {N} - {step title}
Objective: {objective}

Failing tests:
{list of failing test names}

Implement:
{implementation guidance from step file}

Files to create/modify:
{list of files}

Next: Run `pytest tests/test_{feature}.py -v` to verify tests pass
```

#### REFACTOR Phase Output:
```
🔵 REFACTOR Phase: Improve Code Quality

Current Step: {N} - {step title}
All tests passing ✅

Refactoring checklist:
□ Extract common patterns into functions
□ Add type hints to all functions
□ Add docstrings (Google style)
□ Add logging for debugging
□ Remove duplicated code
□ Improve variable/function names
□ Add error handling

Files to refactor:
{list of implementation files}

Next:
- Run full test suite: `pytest tests/ -v`
- Commit: `git commit -m "feat: complete step {N}..."`
- Move to step {N+1}: Use /next-step again
```

## Example Usage

```bash
$ /next-step
```

Output:
```
📍 Active Feature: 02-document-ingestion
📋 Current Step: 03 - Parse and Chunk Documents

🟢 GREEN Phase: Make Tests Pass

Failing tests:
- test_parse_pdf_extracts_text
- test_chunk_text_creates_passages
- test_chunks_have_metadata

Implement these components:

1. Create ingestion/parsers.py:
   - parse_pdf(file_path: str) -> str
   - parse_docx(file_path: str) -> str
   - parse_markdown(file_path: str) -> str

2. Create ingestion/chunker.py:
   - chunk_text(text: str, doc_id: str, filename: str) -> List[Chunk]
   - Use RecursiveCharacterTextSplitter (1000 chars, 200 overlap)

Dependencies to add:
- pdfplumber==0.10.3
- python-docx==1.1.0
- langchain-text-splitters==0.2.2

Next: Run `pytest tests/test_parsers.py tests/test_chunker.py -v`
```

## Special Cases

### Multiple Active Features

If multiple symlinks exist in `.claude/plans/`:
```
Found multiple active features:
1. 02-document-ingestion (step 03)
2. 03-vector-search-rag (step 01)

Which feature are you working on? (1/2)
```

### Feature Complete

If all steps are done:
```
✅ All steps complete for 02-document-ingestion!

Verification checklist:
□ All tests passing
□ All acceptance criteria met
□ Documentation updated
□ No TODO comments remaining

Ready to complete? Use /complete-feature 02-document-ingestion
```

### No Active Features

```
⚠️  No active features found in .claude/plans/

Available features:
- 03-vector-search-rag
- 04-external-search
- 05-answer-synthesis

Start one with: /start-feature {feature-name}
```

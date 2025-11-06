Complete a feature by verifying all acceptance criteria, removing the symlink, and committing the completion.

## Usage

```
/complete-feature 02-document-ingestion
```

## What This Does

1. **Verifies all steps complete**: Ensures all numbered steps (01, 02, 03, etc.) are done
2. **Checks acceptance criteria**: Validates all user story acceptance criteria met
3. **Runs full test suite**: Ensures no regressions
4. **Removes symlink**: Deletes `.claude/plans/{feature-name}-task.plan.md`
5. **Commits completion**: Creates git commit marking feature complete
6. **Suggests next feature**: Shows what to work on next

## Steps

### 1. Validate Feature Name

Check that:
- Feature directory exists in `.work-items/{feature-name}/`
- Symlink exists in `.claude/plans/{feature-name}-task.plan.md`

### 2. Verify All Steps Complete

```bash
# List all step files
ls .work-items/{feature-name}/*_*.md | wc -l

# Count step files
TOTAL_STEPS=$(ls .work-items/{feature-name}/*_*.md | wc -l)
```

For each step, verify:
- [ ] Tests exist for this step
- [ ] Tests pass
- [ ] Implementation complete
- [ ] Code committed

### 3. Check User Story Acceptance Criteria

Read `.work-items/{feature-name}/user-story.md` and extract all "WHEN/THEN/IF" criteria (EARS format).

Verify each criterion has:
- Corresponding test
- Test passes
- Functionality implemented

### 4. Run Full Test Suite

```bash
pytest tests/ -v --tb=short
```

All tests must pass. If any fail:
```
❌ Cannot complete feature: {N} tests failing

Failing tests:
{list failing tests}

Fix these tests before completing the feature.
```

### 5. Design Compliance Check

Read `.work-items/{feature-name}/design.md` and verify:
- [ ] All components mentioned in design are implemented
- [ ] API contracts match design specifications
- [ ] Data models match design
- [ ] Integration points implemented

### 6. Code Quality Final Check

Scan all implementation files:
- [ ] No TODO comments
- [ ] No print() statements
- [ ] All functions have type hints
- [ ] All public functions have docstrings
- [ ] Appropriate logging in place
- [ ] Error handling complete

### 7. Remove Symlink

```bash
rm .claude/plans/{feature-name}-task.plan.md
```

### 8. Create Completion Commit

Calculate time saved and create comprehensive commit:

```bash
git add .claude/plans/
git commit -m "feat: complete {feature-name}

[Detailed summary of feature implementation]

All acceptance criteria met:
✅ Criterion 1
✅ Criterion 2
✅ Criterion 3

Steps completed:
- Step 01: {title}
- Step 02: {title}
- Step 03: {title}
...

Test results:
- Total tests: {N} passed
- Coverage: {%}
- No regressions

⏱️  Time Tracking:
- Total estimated: {X} hours
- Total actual: {Y} hours
- Time saved: {Z} hours ({%} faster)

🤖 Generated with Claude Code
Co-Authored-By: Claude <noreply@anthropic.com>"
```

### 9. Suggest Next Feature

List available features not yet started:

```bash
# List all features
ls .work-items/

# Check which have symlinks (active)
ls .claude/plans/

# Show available features
```

## Output Format

### Verification Phase

```
🔍 Verifying feature completion: {feature-name}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

📋 Steps Completed:

✅ Step 01: File Upload Endpoint (6 tests passing)
✅ Step 02: Link Ingestion Endpoint (6 tests passing)
✅ Step 03: Parse and Chunk Documents (9 tests passing)
✅ Step 04: Generate Embeddings (9 tests passing)
✅ Step 05: Persist Artifacts (13 tests passing)

Total: 5/5 steps complete

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

📝 User Story Acceptance Criteria:

✅ Upload PDF, DOCX, or Markdown files → test_upload_pdf, test_upload_docx, test_upload_markdown
✅ Submit URL for ingestion → test_upload_link
✅ Receive error for unsupported types → test_upload_unsupported_type
✅ Documents parsed into chunks → test_chunk_text_creates_passages
✅ Chunks converted to embeddings → test_embed_texts_batch
✅ Embeddings stored in Qdrant → test_upsert_chunks
✅ Original artifacts saved → test_save_upload, test_save_web_page
✅ Error handling without system failure → test_upload_link_with_firecrawl_error
✅ Search indexed content → test_search_by_query

Total: 9/9 criteria met

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

🎯 Test Suite:

Running full test suite...

tests/test_upload_endpoint.py ........... PASSED
tests/test_link_ingestion.py ........... PASSED
tests/test_parsers.py ............. PASSED
tests/test_chunker.py ............. PASSED
tests/test_embeddings.py ............. PASSED
tests/test_vector_store.py ............... PASSED
tests/test_artifacts.py .................. PASSED
tests/test_pipeline.py ................... PASSED

Total: 68 tests passed
Coverage: 94%
No regressions detected

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

✨ Code Quality:

✅ No TODO comments
✅ No print statements
✅ Type hints complete
✅ Docstrings present
✅ Logging implemented
✅ Error handling complete

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

⏱️  Time Tracking Summary:

Step 01: Estimated 2.5h, Actual 0.75h, Saved 1.75h (70% faster)
Step 02: Estimated 2.5h, Actual 1.0h, Saved 1.5h (60% faster)
Step 03: Estimated 3.0h, Actual 1.0h, Saved 2.0h (67% faster)
Step 04: Estimated 3.0h, Actual 1.25h, Saved 1.75h (58% faster)
Step 05: Estimated 4.0h, Actual 1.5h, Saved 2.5h (63% faster)

Total: Estimated 15h, Actual 5.5h, Saved 9.5h (63% faster)

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

✅ Feature Ready for Completion!

Removing symlink and creating completion commit...
```

### Completion Confirmation

```
✅ Feature Complete: 02-document-ingestion

Symlink removed: .claude/plans/02-document-ingestion-task.plan.md
Commit created: feat: complete 02-document-ingestion

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

📊 Summary:

- 5 steps completed
- 68 tests passing
- 94% code coverage
- 9.5 hours saved (63% faster than estimated)

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

🚀 Next Feature Options:

1. 03-vector-search-rag (Retrieval-augmented generation)
2. 04-external-search (External web search integration)
3. 05-answer-synthesis (Critical reasoning and synthesis)

Start next feature with:
/start-feature {feature-name}
```

## Failure Cases

### Steps Incomplete

```
❌ Cannot complete feature: Not all steps finished

Incomplete steps:
- Step 04: Generate Embeddings (tests not written)
- Step 05: Persist Artifacts (not started)

Complete all steps before finishing the feature.
Use /next-step to continue working.
```

### Acceptance Criteria Not Met

```
❌ Cannot complete feature: Acceptance criteria not met

Missing criteria:
⚠️  "Search indexed content" - No test found
⚠️  "Error handling without failure" - Test failing

Fix these issues before completing the feature.
```

### Tests Failing

```
❌ Cannot complete feature: Tests failing

Failing tests (3):
- tests/test_pipeline.py::test_ingest_file_rollback
- tests/test_vector_store.py::test_delete_by_doc_id
- tests/test_artifacts.py::test_save_web_page

Fix failing tests before completing the feature.
```

### No Active Symlink

```
❌ Feature not active: {feature-name}

No symlink found in .claude/plans/

If this feature is complete, it's already been marked done.
If you want to work on it, use: /start-feature {feature-name}
```

## genai-specs Compliance

This command enforces the genai-specs verification protocol:

> "Prematurely marking tasks as complete can lead to incomplete work and hinder project progress."

The command will NOT allow completion unless:
1. All steps have passing tests
2. All acceptance criteria verified
3. All design components implemented
4. Code quality standards met
5. No regressions in test suite

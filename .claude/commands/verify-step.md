Verify that the current step meets all acceptance criteria before moving to the next step.

## Usage

```
/verify-step
```

## What This Does

1. **Identifies current step**: Determines which step you're verifying
2. **Runs all tests**: Executes test suite to check functionality
3. **Checks acceptance criteria**: Verifies each criterion from the step file
4. **Reviews code quality**: Checks for type hints, docstrings, logging
5. **Validates integration**: Ensures no regressions in other tests
6. **Reports status**: Shows what's complete and what needs work

## Steps

### 1. Find Current Step

Same logic as `/next-step` to identify active feature and current step number.

### 2. Run Tests for This Step

```bash
# Run step-specific tests
pytest tests/test_{feature}.py -v --tb=short

# Check test coverage
pytest tests/test_{feature}.py --cov={module} --cov-report=term-missing
```

### 3. Extract Acceptance Criteria

Read `.work-items/{feature-name}/{N}_*.md` and extract all acceptance criteria.

Example from step file:
```markdown
## Acceptance Criteria
- Endpoint accepts PDF, DOCX, and Markdown files
- Invalid file types return 400 error with clear message
- Valid uploads return ingestion_id
- Background task queues file for processing
```

### 4. Verify Each Criterion

For each criterion, check:
- ✅ Is there a test for this criterion?
- ✅ Does the test pass?
- ✅ Is the functionality complete?

### 5. Code Quality Checklist

Check implementation files for:
- [ ] **Type hints**: All functions have parameter and return type hints
- [ ] **Docstrings**: All public functions have Google-style docstrings
- [ ] **Logging**: Appropriate logging statements (info, warning, error)
- [ ] **Error handling**: Try/except blocks for expected failures
- [ ] **Input validation**: Check for edge cases and invalid inputs
- [ ] **No TODO comments**: All TODOs resolved or removed
- [ ] **No print statements**: Use logging instead of print()

### 6. Integration Verification

Run full test suite to check for regressions:

```bash
pytest tests/ -v --tb=short
```

All existing tests must still pass.

### 7. Generate Report

Output a verification report showing status of all checks.

## Output Format

```
🔍 Verification Report: Step {N} - {step title}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

📝 Acceptance Criteria:

✅ Criterion 1: {description}
   Test: test_criterion_1() - PASSED

✅ Criterion 2: {description}
   Test: test_criterion_2() - PASSED

⚠️  Criterion 3: {description}
   Test: test_criterion_3() - FAILED
   Issue: {error message}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

🎯 Test Results:

Step tests: 12 passed, 1 failed
Coverage: 85% (target: 80%+)
Full suite: 45 passed, 1 failed

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

✨ Code Quality:

✅ Type hints present
✅ Docstrings complete
✅ Logging implemented
⚠️  3 TODO comments found
✅ No print statements
✅ Error handling present

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

📊 Overall Status: ⚠️  NOT READY

Issues to resolve:
1. Fix failing test: test_criterion_3()
2. Resolve TODO comments in app/routes/upload.py:45, 67, 89

Next steps:
- Fix the failing test
- Resolve or remove TODO comments
- Run /verify-step again
```

## Success Output

When all criteria are met:

```
🔍 Verification Report: Step 01 - File Upload Endpoint

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

📝 Acceptance Criteria: ALL MET ✅

✅ Endpoint accepts PDF, DOCX, and Markdown files
✅ Invalid file types return 400 error with clear message
✅ Valid uploads return ingestion_id
✅ Background task queues file for processing
✅ Test verifies ingestion pipeline invocation

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

🎯 Test Results: ALL PASSING ✅

Step tests: 6/6 passed
Coverage: 92%
Full suite: 46/46 passed

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

✨ Code Quality: EXCELLENT ✅

✅ Type hints present
✅ Docstrings complete
✅ Logging implemented
✅ No TODO comments
✅ No print statements
✅ Error handling present

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

📊 Overall Status: ✅ READY TO COMMIT

Suggested commit message:

feat(ingestion): implement file upload endpoint

- Added POST /upload/file endpoint with validation
- Supports PDF, DOCX, and Markdown files
- Returns ingestion_id for tracking
- Queues files for background processing
- Added 6 comprehensive tests (all passing)

Acceptance criteria: All met ✅
Test coverage: 92%

⏱️  Time Tracking:
- Estimated: 2-3 hours
- Actual: [calculate from start time]
- Time saved: [calculate]

🤖 Generated with Claude Code
Co-Authored-By: Claude <noreply@anthropic.com>

Next: Commit this step and move to next with /next-step
```

## Special Cases

### No Active Feature

```
⚠️  No active feature found.

Use /start-feature {name} to begin working on a feature.
```

### Step Not Started

```
⚠️  Step {N} not started yet.

No tests found for this step. Use /next-step to see TDD guidance.
```

### Ready for Next Step

```
✅ Step {N} complete and verified!

All acceptance criteria met. Ready to move to step {N+1}.

Commit this step:
git add .
git commit -m "{suggested message}"

Then use /next-step to continue.
```

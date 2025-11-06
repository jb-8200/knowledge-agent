# Hotfix Protocol Skill

This skill provides guidance for handling critical production bugs using the hotfix workflow.

## When to Invoke

This skill is automatically available when:
- Running as a hotfix subagent (spawned by `/hotfix` command)
- Handling critical production issues
- Need TDD guidance for urgent fixes

## Hotfix Principles

### 1. Speed with Discipline
- **Fast execution** but never skip tests
- **Minimal changes** to reduce risk
- **Clear commits** for easy rollback
- **Full test suite** must still pass

### 2. TDD is Non-Negotiable
Even in emergencies, follow Red → Green → Refactor:
1. **RED**: Write failing test that reproduces bug
2. **GREEN**: Implement minimal fix to pass test
3. **REFACTOR**: (Usually skip for hotfixes - defer to feature work)

### 3. Minimal Viable Fix
- Fix only the immediate issue
- Don't improve or refactor other code
- Don't add features
- Keep diff < 100 lines if possible

## Hotfix Workflow

### Phase 1: Setup (2 min)
```bash
# Create hotfix branch
git checkout -b hotfix/{slug}

# Verify clean state
git status
```

### Phase 2: Reproduce (5-15 min)
```python
# tests/test_{affected_module}.py

def test_bug_reproduction():
    """Reproduce the production bug.

    This test MUST fail initially, proving the bug exists.
    """
    # Arrange: Set up conditions that trigger bug
    # Act: Execute the buggy behavior
    # Assert: Expect correct behavior (will fail initially)

    # Example:
    # result = buggy_function(edge_case_input)
    # assert result == expected_output  # Will fail!
```

**Validation**: Run test, confirm it fails:
```bash
pytest tests/test_{module}.py::test_bug_reproduction -v
# Should see: FAILED
```

### Phase 3: Fix (15-30 min)
```python
# {affected_module}.py

def buggy_function(input_data):
    # OLD CODE (remove):
    # result = process_without_validation(input_data)

    # NEW CODE (add):
    if not validate_input(input_data):
        raise ValueError("Invalid input")
    result = process_with_validation(input_data)

    return result
```

**Key principles**:
- Smallest change possible
- Add validation/error handling
- Fix root cause, not symptoms
- Add logging for debugging

### Phase 4: Verify (5-10 min)
```bash
# Run specific test
pytest tests/test_{module}.py::test_bug_reproduction -v
# Should see: PASSED

# Run full test suite (critical!)
pytest tests/ -v
# All tests must pass
```

### Phase 5: Document (5 min)
```bash
# Update .work-items/00-hotfixes/{id}/fix.md
```

Example `fix.md`:
```markdown
# Fix: {Issue Title}

## Root Cause
{What caused the bug}

Example: Missing null check in vector_store.insert_vectors()
caused NoneType error when chunk_metadata was empty.

## Solution
{What you changed}

Example: Added validation at function entry:
```python
if chunk_metadata is None:
    chunk_metadata = {}
```

## Test Coverage
{Test you added}

Example: test_insert_vectors_with_none_metadata()

## Verification
- ✅ New test passes
- ✅ Full test suite passes (48 tests)
- ✅ No regressions introduced

## Deployment Notes
{Any special considerations}

Example: No migration needed. Backward compatible.
```

### Phase 6: Commit (2 min)
```bash
# Stage changes
git add {affected_files}

# Commit with hotfix prefix
git commit -m "hotfix: {issue description}

Root cause: {one-line cause}
Solution: {one-line solution}

Tests: {test count} passed, 0 failed

Ref: .work-items/00-hotfixes/{id}/

🤖 Generated with Claude Code
Co-Authored-By: Claude <noreply@anthropic.com>"

# Verify commit
git log -1 --stat
```

## Common Hotfix Patterns

### Pattern 1: Missing Validation
```python
# BEFORE (buggy)
def process_data(data):
    return data.upper()  # Crashes if data is None

# AFTER (fixed)
def process_data(data):
    if data is None:
        raise ValueError("data cannot be None")
    return data.upper()

# TEST
def test_process_data_rejects_none():
    with pytest.raises(ValueError, match="cannot be None"):
        process_data(None)
```

### Pattern 2: Resource Leak
```python
# BEFORE (buggy)
def query_database():
    conn = get_connection()
    result = conn.execute(query)
    return result  # Connection never closed!

# AFTER (fixed)
def query_database():
    conn = get_connection()
    try:
        result = conn.execute(query)
        return result
    finally:
        conn.close()  # Always clean up

# TEST
def test_query_database_closes_connection(mocker):
    mock_conn = mocker.patch('module.get_connection')
    query_database()
    mock_conn.return_value.close.assert_called_once()
```

### Pattern 3: Race Condition
```python
# BEFORE (buggy)
def concurrent_update(resource_id):
    resource = db.get(resource_id)
    resource.counter += 1
    db.save(resource)  # Lost update problem!

# AFTER (fixed)
def concurrent_update(resource_id):
    with db.transaction():
        resource = db.get(resource_id, for_update=True)  # Lock
        resource.counter += 1
        db.save(resource)

# TEST
def test_concurrent_update_is_atomic():
    # Use threading to simulate concurrent access
    # Verify counter is correct after N threads
```

### Pattern 4: Timeout Missing
```python
# BEFORE (buggy)
response = requests.get(url)  # Hangs forever if server down

# AFTER (fixed)
response = requests.get(url, timeout=30)  # 30 second timeout

# TEST
def test_api_call_times_out(mocker):
    mocker.patch('requests.get', side_effect=Timeout())
    with pytest.raises(Timeout):
        make_api_call()
```

## Hotfix Anti-Patterns

### ❌ DON'T: Refactor While Fixing
```python
# BAD: Mixing fix with refactoring
def buggy_function(data):
    # Fix the bug
    if data is None:
        data = {}

    # DON'T ALSO REFACTOR:
    # - Rename variables
    # - Extract functions
    # - Reformat code
    # - Add features
```

**Why**: Makes code review harder, increases risk

### ❌ DON'T: Skip Tests
```python
# BAD: "I'll add tests later"
# (You won't, and pre-commit hook will reject it anyway)
```

**Why**: Violates TDD, enables regressions

### ❌ DON'T: Fix Multiple Bugs
```python
# BAD: One commit fixing 3 bugs
# hotfix: fix null check, timeout, and validation
```

**Why**: Hard to review, hard to rollback one fix

**Solution**: Create separate hotfix branches for each bug

### ❌ DON'T: Change Behavior
```python
# BAD: Hotfix that adds new feature
def process_data(data):
    if data is None:
        data = {}

    # DON'T ADD: New caching logic
    # DON'T ADD: New validation rules
    # DON'T ADD: Performance optimizations
```

**Why**: Hotfixes should be surgical, not exploratory

## Edge Cases

### What if I can't write a failing test?
**Situation**: Bug only happens in production with specific data
**Solution**:
1. Mock the production conditions in test
2. Use fixtures to replicate production data
3. If impossible: Document why in fix.md and add manual test steps

### What if fix requires refactoring?
**Situation**: Bug is architectural, quick fix isn't safe
**Solution**:
1. Implement band-aid fix (minimal, safe)
2. Create new feature work item for proper solution
3. Document technical debt in fix.md
4. Schedule proper fix in next sprint

### What if tests fail after fix?
**Situation**: Your fix breaks other tests
**Solution**:
1. Those tests are catching regressions - good!
2. Investigate why they're failing
3. Either:
   - Fix your change (it has unintended side effects)
   - Update tests (if they were testing buggy behavior)

### What if hotfix conflicts with feature work?
**Situation**: Hotfix touches same files as current feature
**Solution**:
1. Complete hotfix first (it's urgent)
2. Merge hotfix to main
3. Rebase feature branch on main
4. Resolve conflicts
5. Re-run feature tests

## Success Criteria

A successful hotfix meets all of these:
- ✅ Has failing test that reproduces bug
- ✅ Test now passes after fix
- ✅ Full test suite still passes
- ✅ Changes are minimal (< 100 lines)
- ✅ Root cause documented in fix.md
- ✅ Commit message follows format
- ✅ No refactoring mixed in
- ✅ Deployed and verified in production

## Reporting Back to Main Agent

When hotfix is complete, report:

```json
{
  "status": "completed",
  "branch": "hotfix/{slug}",
  "commit_sha": "{SHA}",
  "tests_passed": true,
  "test_results": "48 passed, 0 failed",
  "root_cause": "{one sentence}",
  "solution": "{one sentence}",
  "files_changed": ["{file1}", "{file2}"],
  "deployment_notes": "{any special considerations}",
  "next_steps": "Ready to merge to main"
}
```

If hotfix encountered issues:
```json
{
  "status": "partial",
  "branch": "hotfix/{slug}",
  "tests_passed": false,
  "test_results": "46 passed, 2 failed",
  "root_cause": "Partially identified: {description}",
  "blockers": ["Unable to reproduce exact production conditions", "..."],
  "next_steps": "Manual investigation required. See fix.md for details."
}
```

## Time Budget

Typical hotfix timeline:
- **Setup**: 2 minutes
- **Reproduce**: 5-15 minutes
- **Fix**: 15-30 minutes
- **Verify**: 5-10 minutes
- **Document**: 5 minutes
- **Commit**: 2 minutes

**Total**: 30-60 minutes for most hotfixes

If exceeding 2 hours:
- Re-evaluate if this is truly a quick hotfix
- Consider creating full feature work item instead
- May need deeper investigation

## Remember

> The goal is not perfection, but production stability.
> Write the minimal fix that safely resolves the immediate issue.
> Save improvements and optimizations for planned feature work.

## Related

- ADR 001: Edge-Case Handling
- `.claude/commands/hotfix.md` - How to invoke hotfix
- `process-03-development.mdc` - TDD requirements
- `.work-items/00-templates/hotfix-template/` - Templates

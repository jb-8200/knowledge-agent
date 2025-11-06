# Hotfix Command

Handle critical production bugs in parallel with ongoing feature work using a specialized subagent.

## Usage

```
/hotfix <issue-description>
```

## Examples

```
/hotfix "Database deadlock during concurrent file uploads"
/hotfix "Memory leak in embedding service after 1000 requests"
/hotfix "Qdrant connection timeout in production"
```

## What This Does

1. **Creates hotfix work item** with minimal spec:
   - Timestamp-based directory in `.work-items/00-hotfixes/`
   - Generates `incident.md`, `root-cause.md` (placeholder), `fix.md` (placeholder)

2. **Spawns hotfix subagent** via Task tool:
   - Runs independently without blocking main agent
   - Creates hotfix branch: `hotfix/{slug}`
   - Follows TDD cycle: write failing test → implement fix → verify
   - Commits with prefix: `hotfix: {description}`

3. **Reports back status**:
   - Branch name
   - Test results
   - Commit SHA
   - Any errors encountered

## Hotfix Workflow (Automated by Subagent)

```
┌─────────────────────────────────────────────────────┐
│ User: /hotfix "issue description"                   │
└───────────────────┬─────────────────────────────────┘
                    │
        ┌───────────▼────────────┐
        │ Main Agent             │
        │ Creates work item      │
        │ Spawns subagent        │
        │ CONTINUES feature work │ ← Non-blocking!
        └───────────┬────────────┘
                    │
        ┌───────────▼────────────┐
        │ Hotfix Subagent        │
        │ 1. Create branch       │
        │ 2. Write failing test  │
        │ 3. Implement fix       │
        │ 4. Run full test suite │
        │ 5. Commit changes      │
        │ 6. Report status       │
        └───────────┬────────────┘
                    │
        ┌───────────▼────────────┐
        │ Main Agent             │
        │ Receives report        │
        │ Can review/merge       │
        └────────────────────────┘
```

## Prerequisites

Before running this command, ensure:
- You have a clear description of the production issue
- The issue is truly critical (production impact)
- For non-critical issues, use regular feature workflow

## Steps Performed

### 1. Generate Unique ID

Create timestamp-based identifier:
```bash
timestamp=$(date +%Y%m%d-%H%M%S)
slug=$(echo "issue description" | tr '[:upper:]' '[:lower:]' | sed 's/[^a-z0-9]/-/g' | sed 's/--*/-/g')
hotfix_id="${timestamp}-${slug}"
```

### 2. Create Work Item Directory

```bash
mkdir -p .work-items/00-hotfixes/${hotfix_id}
cd .work-items/00-hotfixes/${hotfix_id}
```

### 3. Generate Incident Report

Create `incident.md` from template:
```markdown
# Incident Report: {issue description}

## Discovery
- **Reported**: {timestamp}
- **Environment**: Production
- **Severity**: Critical

## Impact
{user-provided description}

## Symptoms
- {what users are experiencing}

## Affected Components
- {components/files affected}

## Timeline
- {timestamp}: Issue discovered
- {timestamp}: Hotfix initiated
```

### 4. Spawn Hotfix Subagent

Invoke Task tool with specialized prompt:
```python
task_result = Task(
    subagent_type="general-purpose",
    model="sonnet",  # Need full reasoning for fixes
    description=f"Fix critical bug: {issue_description}",
    prompt=f"""
You are a hotfix specialist working on a critical production issue.

ISSUE: {issue_description}

Your mission:
1. Create hotfix branch: `hotfix/{slug}`
2. Analyze the issue and identify root cause
3. Write a FAILING test that reproduces the bug
4. Implement minimal fix to make test pass
5. Run full test suite to ensure no regressions
6. Commit with message: "hotfix: {issue_description}"
7. Update `.work-items/00-hotfixes/{hotfix_id}/` with findings

Follow TDD strictly. The pre-commit hook will enforce tests.

Report back:
- Branch name
- Test results (pass/fail counts)
- Commit SHA
- Root cause identified
- Any issues encountered
"""
)
```

### 5. Continue Main Work

Main agent returns immediately and continues feature development.
Subagent runs in parallel.

### 6. Process Subagent Results

When subagent completes, main agent receives:
```json
{
  "status": "completed",
  "branch": "hotfix/database-deadlock-concurrent-uploads",
  "commit_sha": "abc123def456",
  "tests_passed": true,
  "test_results": "48 passed, 0 failed",
  "root_cause": "Missing transaction isolation in vector_store.insert_vectors()",
  "files_changed": [
    "ingestion/vector_store.py",
    "tests/test_vector_store.py"
  ],
  "notes": "Added database lock with 5s timeout to prevent concurrent insert conflicts"
}
```

Main agent can then:
- Display summary to user
- Optionally review changes
- Merge hotfix branch
- Continue with current work

## Output Format

### Success Case
```
🔥 Hotfix initiated: database-deadlock-concurrent-uploads

📁 Work item: .work-items/00-hotfixes/20251106-135045-database-deadlock/
🤖 Subagent spawned (running in parallel)

[Main agent continues with F03 vector search work...]

─────────────────────────────────────────────────────

🎯 Hotfix complete!

✅ Branch: hotfix/database-deadlock-concurrent-uploads
✅ Tests: 48 passed, 0 failed
✅ Commit: abc123d

Root cause: Missing transaction isolation in vector_store.insert_vectors()

Files changed:
- ingestion/vector_store.py
- tests/test_vector_store.py

Ready to merge hotfix branch when you're ready.
```

### Error Case
```
🔥 Hotfix initiated: memory-leak-embedding-service

📁 Work item: .work-items/00-hotfixes/20251106-140122-memory-leak/
🤖 Subagent spawned (running in parallel)

─────────────────────────────────────────────────────

⚠️  Hotfix encountered issues

❌ Tests failed: 2 failing, 46 passing
🔍 Root cause: Could not isolate leak source

The subagent created a draft fix on branch hotfix/memory-leak-embedding-service
but tests are still failing. Manual investigation required.

Check: .work-items/00-hotfixes/20251106-140122-memory-leak/root-cause.md
```

## Best Practices

### When to Use /hotfix
✅ **DO use for**:
- Production outages
- Data corruption issues
- Security vulnerabilities
- Critical performance degradations
- Customer-blocking bugs

❌ **DON'T use for**:
- Feature enhancements
- Non-urgent bugs
- Refactoring
- Performance optimizations (unless critical)
- Issues that need investigation

### TDD Still Required
Even in emergencies, write the failing test first:
- Proves the bug exists
- Prevents regression
- Documents expected behavior
- Enforced by pre-commit hook

### Minimal Fix Philosophy
- Fix only what's broken
- Don't refactor or improve other code
- Don't add features while fixing bugs
- Keep changes reviewable (< 100 lines ideal)

### Post-Hotfix Actions
After subagent completes:
1. **Review** the fix (read the code changes)
2. **Test** in staging if available
3. **Merge** to main branch
4. **Deploy** immediately
5. **Monitor** for resolution
6. **Document** root cause fully
7. **Update** affected feature specs to prevent recurrence

## Integration with Main Workflow

### Parallel Execution Example
```
Time    Main Agent                 Hotfix Subagent
────    ──────────────────────     ─────────────────────────
10:00   Working on F03 Step 02
10:15   User: /hotfix "deadlock"
10:15   Spawns subagent            Starts working on fix
10:16   Continues F03 Step 02      Creates branch, writes test
10:30   Still on F03 Step 02       Implements fix
10:35   Still on F03 Step 02       Commits, runs tests
10:40   Receives hotfix report     Reports: "Fixed, tests pass"
10:41   Reviews hotfix summary
10:42   Continues F03 Step 02      [Done]
```

### No Context Switching
- Main agent's context preserved
- No interruption to feature work
- Hotfix runs independently
- Both can commit to different branches

## Troubleshooting

### Subagent Fails to Start
If subagent doesn't spawn:
- Check Task tool availability
- Verify .work-items/ directory exists
- Ensure issue description is clear

### Tests Fail After Fix
If subagent reports failing tests:
- Review `.work-items/00-hotfixes/{id}/root-cause.md`
- Check branch: `git checkout hotfix/{slug}`
- Run tests manually: `pytest tests/ -v`
- May need manual investigation

### Merge Conflicts
If hotfix conflicts with main:
- Checkout hotfix branch
- Rebase on main: `git rebase main`
- Resolve conflicts
- Re-run tests
- Force push if needed: `git push -f origin hotfix/{slug}`

## Related

- ADR 001: Edge-Case Handling
- `.claude/skills/hotfix-protocol/` - Hotfix TDD guidance
- `.work-items/00-templates/hotfix-template/` - Templates
- `process-03-development.mdc` - TDD requirements

## Implementation Note

This command uses Claude Code's Task tool to spawn a subagent with `subagent_type="general-purpose"`. The subagent has full access to all tools (Bash, Read, Write, Edit) and can perform git operations independently.

The key innovation is **non-blocking parallel execution**: the main agent continues feature work while the subagent handles the hotfix.

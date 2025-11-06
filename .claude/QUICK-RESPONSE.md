# Quick Response Guide: Handling Unplanned Work

Quick reference for deciding how to handle critical bugs, discovered issues, and plan changes during spec-driven development.

## Decision Flowchart

```
┌──────────────────────────────────────────┐
│ UNPLANNED WORK ARRIVES                   │
└───────────────┬──────────────────────────┘
                │
        ┌───────▼──────────┐
        │ Is it CRITICAL?  │
        │ (prod down/      │
        │  data loss/      │
        │  security)       │
        └────┬────────┬────┘
             │YES     │NO
             │        │
    ┌────────▼─────┐  │
    │  /hotfix     │  │
    │  (parallel)  │  │
    └──────────────┘  │
                      │
              ┌───────▼────────────┐
              │ Discovered during  │
              │ feature work?      │
              └────┬───────────┬───┘
                   │YES        │NO
                   │           │
         ┌─────────▼────┐   ┌─▼──────────────┐
         │ How big?     │   │ Requirements   │
         │ How related? │   │ changed?       │
         └┬────┬────┬───┘   └┬───────────┬───┘
          │    │    │        │YES        │NO
       < 15  <1h  >1h        │           │
        min        │         │      ┌────▼────┐
          │        │         │      │ Defer   │
      ┌───▼───┐ ┌─▼───────┐ │      │ Create  │
      │ Do    │ │ Add as  │ │      │ backlog │
      │ now   │ │ step to │ │      │ item    │
      └───────┘ │ feature │ │      └─────────┘
                └─────────┘ │
                            │
                 ┌──────────▼─────────┐
                 │ Use PIVOT protocol │
                 │ Small/Major/Cancel │
                 └────────────────────┘
```

## Quick Reference Table

| Scenario | Time | Action | Command | Branch |
|----------|------|--------|---------|--------|
| **Production down** | Any | Hotfix subagent | `/hotfix` | `hotfix/*` |
| **Data corruption** | Any | Hotfix subagent | `/hotfix` | `hotfix/*` |
| **Security vuln** | Any | Hotfix subagent | `/hotfix` | `hotfix/*` |
| **Typo in docs** | < 15 min | Fix now | N/A | Current |
| **Missing validation** | < 1 hour | Add as step | `/next-step` | Current |
| **Needs refactor** | > 1 hour | Defer | Create work item | N/A |
| **Requirements shift** | N/A | Pivot protocol | Update specs | Current/new |
| **Feature cancelled** | N/A | Document | Create CANCELLED.md | N/A |

## Critical Bugs (Use `/hotfix`)

### When to Use
✅ Production outages
✅ Data corruption
✅ Security vulnerabilities
✅ Customer-blocking bugs
✅ Regulatory compliance issues

### Process
```bash
# User invokes
/hotfix "Database deadlock in concurrent uploads"

# What happens:
# 1. Creates .work-items/00-hotfixes/{timestamp-slug}/
# 2. Spawns subagent in parallel
# 3. Subagent: creates branch, writes test, fixes, commits
# 4. Main agent: continues feature work (non-blocking!)
# 5. Subagent reports back: "Fixed on hotfix/database-deadlock"
```

### Characteristics
- **Parallel execution**: Main agent continues working
- **TDD enforced**: Must write failing test first
- **Minimal changes**: < 100 lines ideal
- **Fast turnaround**: 30-60 minutes typical

## Discovered Issues (During Feature Work)

### Tier 1: Trivial & Safe (< 15 min, no risk)

**Examples**:
- Fix typo in error message
- Add missing docstring
- Update outdated comment
- Fix formatting

**Action**: Do immediately
```bash
# Just fix it
git add {file}
git commit -m "feat: add feature X (also: fixed typo in README)"
```

### Tier 2: Small & Related (< 1 hour, same feature)

**Examples**:
- Missing validation in adjacent function
- Similar bug in related module
- Edge case in same component

**Action**: Add as numbered step
```bash
# Create new step file
.work-items/{feature}/04_discovered_validation.md

# Complete as part of feature
# Separate commit from main step
git commit -m "feat({feature}): add discovered validation"
```

### Tier 3: Substantial or Unrelated (> 1 hour or different domain)

**Examples**:
- Performance optimization needed
- Refactoring unrelated module
- New feature idea
- Architectural change

**Action**: Defer and document
```bash
# Add TODO in code
# TODO: Optimize query performance (see .work-items/XX-perf-optimization)

# Create new work item
mkdir .work-items/15-discovered-perf-opt
# Full spec: user-story.md, design.md, task.md

# Update current feature
# In design.md, add to "Out of Scope" section
```

## Plan Changes

### Small Change (Single step affected)

**Action**: Update specs, reset if needed
```bash
# 1. Pause current step
# 2. Update specs
vim .work-items/{feature}/user-story.md  # Fix acceptance criteria
vim .work-items/{feature}/design.md      # Update approach
vim .work-items/{feature}/task.md        # Modify affected step

# 3. Commit spec changes
git add .work-items/{feature}/
git commit -m "plan: revise {feature} to use hybrid search

Changed requirements: Need keyword + semantic search.
Updated design and step 01."

# 4. Reset work if needed
git reset --hard HEAD~1  # If step was wrong

# 5. Resume TDD
```

### Major Change (Multiple steps affected)

**Action**: Pause and create v2
```bash
# 1. Complete current step if almost done

# 2. Pause feature
rm .claude/plans/{feature}-task.plan.md
git commit -m "plan: pause {feature} for requirements review"

# 3. Create revision
cp -r .work-items/{feature} .work-items/{feature}-v2
# Edit v2 specs with new approach

# 4. Document decision
# Create ADR explaining why

# 5. Restart when ready
ln -s ../../.work-items/{feature}-v2/task.md \
      .claude/plans/{feature}-v2-task.plan.md
```

### Fundamental Pivot (Feature cancelled)

**Action**: Document and archive
```bash
# 1. Document why
# Create docs/decisions/XXX-cancel-feature-X.md

# 2. Mark as cancelled
echo "CANCELLED: {reason}" > .work-items/{feature}/CANCELLED.md

# 3. Keep code in history (don't delete)

# 4. Remove from roadmap
```

## Git Commit Patterns

```bash
# Hotfix
hotfix: add timeout to Qdrant client

# Trivial fix alongside feature work
feat: add search endpoint (also: fixed typo in README)

# Related discovered issue
feat(F03): add discovered validation to search

# Deferred work
docs: add TODO for performance optimization

# Spec change
plan: revise F03 to use hybrid search

# Feature pause
plan: pause F04 for requirements review

# Feature cancellation
plan: cancel F04 external search feature
```

## Principles (Never Compromise)

| Principle | Always | Never |
|-----------|--------|-------|
| **TDD** | Write test first | Skip tests |
| **Small batches** | One concern per commit | Mega-commits |
| **Document** | Explain "why" | Hide changes |
| **Git history** | Preserve truth | Rewrite history |
| **Update specs** | Retroactively if needed | Leave stale |

## Red Flags

🚩 **Calling planned work a "hotfix"** → Use feature workflow
🚩 **Skipping tests "just this once"** → Pre-commit hook will reject
🚩 **Fixing 3 bugs in one commit** → Separate hotfixes
🚩 **Refactoring during hotfix** → Defer to feature work
🚩 **Changing behavior as "fix"** → That's a feature

## Time Budgets

| Type | Typical Time | Max Time | If Exceeded |
|------|-------------|----------|-------------|
| Hotfix | 30-60 min | 2 hours | Convert to feature |
| Trivial | 5-15 min | 15 min | Move to Tier 2 |
| Related | 30-60 min | 1 hour | Move to Tier 3 |
| Substantial | N/A | N/A | Full feature workflow |

## Parallel Work Example

```
Time    Main Agent                 Hotfix Subagent
────    ──────────────────────     ─────────────────────────
10:00   Working on F03 Step 02
10:15   User: /hotfix "deadlock"
10:15   Spawns subagent            Starts hotfix
10:16   Continues F03 Step 02      Creates branch
10:30   Still on F03 Step 02       Writes test
10:35   Still on F03 Step 02       Implements fix
10:40   Receives report            Commits, done
10:41   Reviews hotfix
10:42   Continues F03 Step 02

Result: Feature work NEVER BLOCKED by hotfix!
```

## Related Documentation

- **ADR 001**: Edge-Case Handling (full details)
- **`.claude/commands/hotfix.md`**: Hotfix command reference
- **`.claude/skills/hotfix-protocol/`**: TDD guidance for hotfixes
- **`process-03-development.mdc`**: Core TDD and commit standards

## Quick Commands

```bash
# Start hotfix (parallel execution)
/hotfix "issue description"

# Check current step
/next-step

# Verify acceptance criteria
/verify-step

# Complete feature
/complete-feature {name}

# Test RAG pipeline
/test-rag "query"
```

## When in Doubt

Ask yourself:
1. **Is production down?** → `/hotfix`
2. **Can I fix in < 15 min?** → Do now
3. **Related to current feature?** → Add as step
4. **Unrelated or big?** → Defer

**Default**: When unsure, **defer and document**. It's better to be deliberate than rushed.

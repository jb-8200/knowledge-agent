# ADR 001: Edge-Case Handling in Spec-Driven Development

## Status
Accepted

## Date
2025-11-06

## Context
The knowledge-agent project follows a rigorous spec-driven development methodology based on genai-specs, with a formal workflow: user-story → design → task → TDD implementation. This works excellently for planned features but doesn't address:

1. **Critical bugs** requiring immediate production fixes
2. **Out-of-scope issues** discovered during feature implementation
3. **Plan changes** when requirements shift mid-development
4. **Parallel work** needed when bugs arise during feature development

The spec-driven workflow's strength (comprehensive planning) becomes a weakness when urgent, unplanned work is required.

## Decision
We will implement a **three-track system** for handling edge cases while preserving the core principles of TDD, small batches, and documentation:

### Track 1: Hotfix Track (Critical Bugs)
**For**: Production issues, security vulnerabilities, data corruption

**Process**:
1. **Immediate Response** (skip formal planning):
   - Create hotfix branch: `hotfix/{bug-name}`
   - Write failing test that reproduces the bug (TDD still applies)
   - Implement minimal fix to make test pass
   - Run full test suite
   - Commit with prefix: `hotfix: {description}`

2. **Lightweight Documentation**:
   ```
   .work-items/00-hotfixes/{timestamp}-{slug}/
   ├── incident.md      # What broke, impact, when discovered
   ├── root-cause.md    # Why it broke (post-fix analysis)
   └── fix.md           # What was changed
   ```

3. **Process Improvement**:
   - Document root cause
   - Update affected feature specs with lessons learned
   - Add regression test to feature test suite

**Parallel Execution**:
- Hotfix subagent handles fix independently
- Main agent continues feature work
- No blocking or context switching required

### Track 2: Discovered Issues (During Implementation)
**For**: Issues found while implementing features

**Three-Tier Decision Framework**:

#### Tier 1: Trivial & Safe (< 15 min, no risk)
- **Action**: Fix immediately as part of current work
- **Examples**: Typos, missing docstrings, outdated comments
- **Documentation**: Mention in commit: `(also: fixed typo in...)`

#### Tier 2: Small & Related (< 1 hour, related to current feature)
- **Action**: Add as numbered step to current feature
- **Structure**: Create `XX_discovered_{name}.md` in feature's work-items
- **Examples**: Missing validation in adjacent function, similar bug
- **Documentation**: Complete as part of feature, separate commit

#### Tier 3: Substantial or Unrelated (> 1 hour or different domain)
- **Action**: Defer and document
- **Structure**: Create new work item: `.work-items/XX-discovered-{name}/`
- **Documentation**:
  - Update current feature's `design.md` "Out of Scope" section
  - Add TODO comment in code
  - Create full spec when prioritized
- **Examples**: Performance optimization, refactoring unrelated modules

**Decision Tree**:
```
Is it < 15 min and zero risk?
  └─ YES → Do now, mention in commit
  └─ NO → Is it < 1 hour and related to current feature?
      └─ YES → Add as numbered step
      └─ NO → Create new work item, defer
```

### Track 3: Plan Changes (Requirements Shift)
**For**: Specification changes during implementation

#### Small Changes (Single step affected):
1. Pause current step if it's now wrong
2. Update specs in order: `user-story.md` → `design.md` → `task.md`
3. Commit spec changes: `plan: revise {feature} to {new approach}`
4. Reset incomplete work if needed: `git reset --hard HEAD~N`
5. Resume TDD cycle with updated specs

#### Major Changes (Multiple steps or scope):
1. Complete current step if almost done (don't waste TDD work)
2. Mark feature as paused: Remove `.claude/plans/` symlink
3. Create revision work item: `.work-items/{feature}-v2/`
4. Document decision: Create ADR explaining change
5. Restart with clean slate when ready

#### Fundamental Pivot (Feature no longer needed):
1. Document decision in ADR
2. Add `CANCELLED.md` to work item explaining why
3. Keep code in git history (don't delete)
4. Update roadmap to mark as deferred

## Consequences

### Positive
- **Maintains TDD discipline** even in emergencies
- **Preserves documentation** for all work (including hotfixes)
- **Enables parallel work** via subagent architecture
- **Provides clear decision framework** reducing cognitive load
- **Keeps spec-driven workflow intact** for planned features
- **Git history remains clean** with clear commit patterns

### Negative
- **Additional cognitive overhead** of deciding which track to use
- **More directories** in `.work-items/` for hotfixes and discovered issues
- **Requires discipline** to document even quick fixes
- **Potential for abuse** (calling planned work a "hotfix")

### Mitigations
- Clear tier thresholds (15 min, 1 hour) reduce ambiguity
- Pre-commit hooks still enforce TDD (can't skip tests)
- Hotfix command automates process (reduces manual steps)
- Regular review of hotfix work items in retros

## Commit Patterns

| Type | Prefix | Example |
|------|--------|---------|
| Hotfix | `hotfix:` | `hotfix: add timeout to Qdrant client` |
| Trivial | `(also: ...)` | `feat: add search (also: fixed typo in README)` |
| Related | `feat:` or `fix:` | `feat(F03): add discovered validation to search` |
| Deferred | `docs:` | `docs: add TODO for performance optimization` |
| Plan Change | `plan:` | `plan: revise F03 to use hybrid search` |
| Cancellation | `plan:` | `plan: cancel F04 external search feature` |

## Principles Never Compromised

1. **TDD is mandatory** - Write failing test first, even in emergencies
2. **Small batches** - Don't let urgency create mega-commits
3. **Document the "why"** - Future self needs context
4. **Git history is truth** - Never rewrite to hide changes
5. **Update specs retroactively** - If you improvised, document it

## Implementation

See:
- `.claude/commands/hotfix.md` - Hotfix command for parallel execution
- `.claude/skills/hotfix-protocol/` - Hotfix TDD guidance
- `.work-items/00-templates/hotfix-template/` - Hotfix spec templates
- `.claude/QUICK-RESPONSE.md` - Quick reference flowcharts

## Related
- ADR 000: Change Management (if created)
- `process-03-development.mdc` - Core TDD and commit standards
- `standards-task.mdc` - Task breakdown requirements

## Review Date
2025-12-06 (1 month) - Assess if framework is being followed, adjust thresholds if needed

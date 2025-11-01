# Active Work Tracking (.claude/plans/)

**Purpose**: Track which features are currently being actively developed

**Pattern**: Adapted from genai-specs Cursor Plans for Claude Code

**Note**: This is the **single source of truth** for progress monitoring and time tracking workflows. Other files (`PROJECT_STRUCTURE.md`, `.claude/DEVELOPMENT.md`) provide brief overviews with references to this document for detailed information.

---

## Overview

This directory contains **symbolic links** to task files in `.work-items/` for features that are **actively being worked on**. This provides a clear, git-tracked indicator of development status without duplicating content.

**Key Principle**: Symlink presence = active work, symlink absence = complete or not started

---

## How It Works

### File Structure

```
.claude/plans/
├── README.md (this file)
├── 01-project-setup-task.plan.md → ../../.work-items/01-project-setup/task.md
└── 02-document-ingestion-task.plan.md → ../../.work-items/02-document-ingestion/task.md
```

### Symlink Naming Convention

**Format**: `{feature-name}-task.plan.md`

**Examples**:
- `01-project-setup-task.plan.md`
- `02-document-ingestion-task.plan.md`
- `05-answer-synthesis-task.plan.md`

**Target**: Always points to `../../.work-items/{feature-name}/task.md`

---

## Lifecycle Management

### Starting Work on a Feature

**Manual approach**:
```bash
cd .claude/plans
ln -s ../../.work-items/01-project-setup/task.md 01-project-setup-task.plan.md
```

**Script approach** (recommended):
```bash
./scripts/start-feature.sh 01-project-setup
```

**What this does**:
- Creates symlink in `.claude/plans/`
- Indicates feature is now active
- Git tracks the symlink addition
- Edits to task.md sync automatically

### Completing a Feature

**Manual approach**:
```bash
rm .claude/plans/01-project-setup-task.plan.md
```

**Script approach** (recommended):
```bash
./scripts/complete-feature.sh 01-project-setup
```

**What this does**:
- Removes symlink from `.claude/plans/`
- Indicates feature is complete
- Git tracks the symlink removal
- Original task.md remains in `.work-items/`

### Pausing Work

Same as completing - remove the symlink. Re-create it when resuming.

---

## Time Tracking

### Purpose

Track development efficiency by comparing estimated vs actual time for each step.

### How It Works

**Estimates**: Each `task.md` file includes time estimates per step (e.g., "2-3 hours")

**Actual Time**: Calculate from timestamps or active work tracking
- **Start**: When work begins on a step (e.g., Red Phase)
- **End**: When step completion commit is made
- **Midpoint**: Use average of estimate range for comparison

**Commit Message Format**:

```
⏱️  Time Tracking:
- Estimated: 2-3 hours
- Actual: 45 minutes
- Time saved: 1.75 hours (70% faster than estimate)
```

### Benefits

- **Visibility**: See actual productivity gains from Claude Code + TDD
- **Planning**: Improve future estimates based on actual data
- **Motivation**: Celebrate efficiency improvements
- **Reporting**: Demonstrate ROI of development process

### Example Calculation

For F02 Step 01 (File Upload Endpoint):
- **Estimated**: 2-3 hours (midpoint: 2.5 hours)
- **Actual**: ~45 minutes of active work
- **Saved**: 1.75 hours (70% faster)
- **Method**: Based on conversation flow and git commits

**Note**: Git timestamps may not reflect breaks or full development cycle. Track active work time when possible.

### Adding to Commits

Include time tracking at the end of step completion commits:

```bash
git commit -m "feat: implement feature X

[implementation details]

⏱️  Time Tracking:
- Estimated: 2-3 hours
- Actual: 45 minutes
- Time saved: 1.75 hours (70% faster than estimate)

🤖 Generated with [Claude Code](https://claude.com/claude-code)
"
```

---

## Checking Active Work

### List All Active Features

```bash
ls -la .claude/plans/
```

**Output shows**:
- Which features are in progress
- When work started (file creation time)
- Target paths to canonical task files

### Count Active Features

```bash
ls .claude/plans/*.plan.md 2>/dev/null | wc -l
```

### View Active Task Details

```bash
# Read through symlink
cat .claude/plans/01-project-setup-task.plan.md

# Or edit (changes sync to original)
code .claude/plans/01-project-setup-task.plan.md
```

---

## Benefits

✅ **Single Source of Truth**: Edits sync automatically to `.work-items/`
✅ **Easy Discovery**: All active work visible in one directory
✅ **Clear Lifecycle**: Symlink presence = active, absence = done
✅ **Version Control Friendly**: Git tracks symlinks, showing work status
✅ **No Duplication**: Never maintain separate copies
✅ **genai-specs Aligned**: Follows Cursor Plans pattern
✅ **IDE Agnostic**: Works with any editor or IDE

---

## Rules and Best Practices

### ✅ DO

- Create symlink when starting active development
- Remove symlink when feature complete or paused
- Commit symlink changes to git
- Use helper scripts for consistency
- Keep symlinks pointing to `task.md` files only

### ❌ DON'T

- Don't create symlinks for features not actively being worked on
- Don't leave "stale" symlinks for abandoned work
- Don't modify the `.work-items/` structure through plans directory
- Don't create symlinks to individual step files (only task.md)
- Don't use this as a replacement for git commit history

---

## Verification Before Completion

Before removing a symlink (marking feature complete), verify:

1. **All acceptance criteria met** (from user-story.md)
2. **All tests passing** (test strategy executed)
3. **All numbered steps complete** (01, 02, 03, etc.)
4. **Design implemented** (as specified in design.md)
5. **Code committed** (all changes in version control)

**From genai-specs**:
> "Prematurely marking tasks as complete can lead to incomplete work and hinder project progress."

---

## Integration with Development Workflow

### Starting a New Feature

1. Read user-story.md, design.md, task.md
2. Run: `./scripts/start-feature.sh {feature-name}`
3. Commit: `git add .claude/plans/ && git commit -m "Start {feature-name}"`
4. Begin TDD cycle on first numbered step

### During Development

- Edit task.md through symlink or directly in `.work-items/`
- Complete numbered steps (01_step.md, 02_step.md, etc.)
- Commit frequently (each step = 1 commit)
- Run tests continuously

### Completing a Feature

1. Verify all acceptance criteria met
2. Run: `./scripts/complete-feature.sh {feature-name}`
3. Commit: `git add .claude/plans/ && git commit -m "Complete {feature-name}"`
4. Original task.md remains in `.work-items/` as documentation

---

## Example Workflow

```bash
# 1. Check what's currently active
ls .claude/plans/
# (no active work)

# 2. Start project setup feature
./scripts/start-feature.sh 01-project-setup
# Created: .claude/plans/01-project-setup-task.plan.md

# 3. Commit the start
git add .claude/plans/
git commit -m "Start F01: project-setup"

# 4. Work through numbered steps
# ... implement 01_init_repo.md
# ... implement 02_create_env.md

# 5. Verify completion
cat .work-items/01-project-setup/user-story.md  # Check criteria
pytest tests/                                     # Run tests

# 6. Mark complete
./scripts/complete-feature.sh 01-project-setup
# Removed: .claude/plans/01-project-setup-task.plan.md

# 7. Commit the completion
git add .claude/plans/
git commit -m "Complete F01: project-setup - all criteria met"

# 8. Move to next feature
./scripts/start-feature.sh 02-document-ingestion
```

---

## genai-specs Alignment

This pattern is adapted from **genai-specs Cursor Plans**:

**Original (Cursor IDE)**:
```
.cursor/plans/
└── feature-name-task.plan.md → ../../.work-items/feature-name/task.md
```

**Adapted (Claude Code)**:
```
.claude/plans/
└── feature-name-task.plan.md → ../../.work-items/feature-name/task.md
```

**Why the adaptation**:
- Cursor IDE has built-in plans integration
- Claude Code doesn't have equivalent feature
- Using `.claude/` maintains consistency with other Claude Code config
- Pattern and benefits remain identical

---

## Progress Monitoring

### Manual Monitoring

```bash
# What's active?
ls .claude/plans/

# What's defined but not started?
ls .work-items/
# (compare against plans/)

# What's complete?
git log --all -- .claude/plans/ | grep "Complete"
```

### Git-Based Monitoring

```bash
# When did work start on feature X?
git log --all -- .claude/plans/01-project-setup-task.plan.md

# Which features were worked on this week?
git log --since="1 week ago" -- .claude/plans/

# Show development timeline
git log --oneline --all -- .claude/plans/
```

---

## Troubleshooting

### Symlink Broken

**Problem**: Symlink points to non-existent file

**Solution**:
```bash
# Remove broken symlink
rm .claude/plans/broken-link.plan.md

# Recreate correctly
./scripts/start-feature.sh correct-feature-name
```

### Multiple Active Features

**Not a problem**: You can have multiple symlinks for concurrent work

**Example**:
```
.claude/plans/
├── 01-project-setup-task.plan.md
├── 02-document-ingestion-task.plan.md
└── 03-vector-search-rag-task.plan.md
```

**Recommendation**: Focus on 1-3 features at a time (small batch sizes)

### Forgot to Remove Symlink

**Problem**: Feature complete but symlink still exists

**Solution**:
```bash
# Remove manually
rm .claude/plans/01-project-setup-task.plan.md

# Or use script
./scripts/complete-feature.sh 01-project-setup

# Commit the change
git add .claude/plans/ && git commit -m "Mark 01-project-setup complete"
```

---

## References

- **genai-specs**: https://github.com/betsalel-williamson/genai-specs
- **Cursor Plans**: `.cursor/plans/` directory pattern
- **ACID Tasks**: `rules/standards-task.mdc`
- **Verification Protocol**: `rules/guidelines-verification-protocol.mdc`
- **Project Structure**: `PROJECT_STRUCTURE.md`

---

**Last Updated**: November 1, 2025
**Status**: Ready for use

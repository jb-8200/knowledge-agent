# 📦 Archived: Old Plan Structure

**Archived Date**: November 1, 2025
**Reason**: Migrated to genai-specs feature-based workflow

## Contents

This directory contains the **original project planning files** before migration to the genai-specs workflow:

```
old_plan/
├── tasks/              # 36 individual task files + README
├── specs/              # 36 individual spec files + README
└── acceptance_tests/   # 36 individual test files + README
```

## Why Archived?

These files have been **superseded** by the new feature-based structure in `.work-items/` which provides:

- ✅ **User-centric approach** (user stories with personas)
- ✅ **Feature-based organization** (related tasks grouped)
- ✅ **Consolidated documentation** (specs integrated into design docs)
- ✅ **TDD methodology** (test-driven development workflow)
- ✅ **genai-specs compliance** (industry best practices)

## Migration Details

### Complete Mapping

All 36 tasks, 36 specs, and 36 tests have been migrated:

| Old Files | New Location | Feature |
|-----------|-------------|---------|
| tasks/task_01-02.md | .work-items/01-project-setup/ | F01 |
| tasks/task_03-07.md | .work-items/02-document-ingestion/ | F02 |
| tasks/task_08-10.md | .work-items/03-vector-search-rag/ | F03 |
| tasks/task_11-13.md | .work-items/04-external-search/ | F04 |
| tasks/task_14-17.md | .work-items/05-answer-synthesis/ | F05 |
| tasks/task_18-20.md | .work-items/06-web-ui/ | F06 |
| tasks/task_21.md | .work-items/07-youtube-thumbnails/ | F07 |
| tasks/task_22.md | .work-items/08-similar-questions/ | F08 |
| tasks/task_23.md | .work-items/09-pin-answers/ | F09 |
| tasks/task_24.md | .work-items/10-download-markdown/ | F10 |
| tasks/task_25-27.md | .work-items/11-deployment/ | F11 |
| tasks/task_28-30.md | .work-items/12-testing-feedback/ | F12 |
| tasks/task_31-36.md | .work-items/13-spec-driven-integration/ | F13 |

See `MIGRATION_VALIDATION.md` for complete verification report.

## Usage

### ⚠️ These files are for REFERENCE ONLY

- **DO NOT** edit these files
- **DO NOT** use as canonical source
- **DO USE** `.work-items/` for all new work

### When to Reference

You may reference these files to:
- Compare original task descriptions
- Verify migration accuracy
- Understand historical context
- Reference original technical details

### New Workflow

For all development work, use:

1. **Browse features**: `.work-items/{feature-name}/`
2. **Read user story**: Understand user value
3. **Review design**: See technical approach
4. **Follow tasks**: Implement with TDD
5. **Verify acceptance**: Check criteria

## Validation

✅ **Migration validated**: See `MIGRATION_VALIDATION.md`

All original content has been:
- Mapped to appropriate features
- Enhanced with user stories
- Consolidated into design documents
- Integrated with TDD methodology
- Verified for completeness

## Safe to Delete?

**Recommendation**: **Keep for now** (90 days)

These files serve as backup and reference during the transition period. After the team is comfortable with the new structure (suggested: 3 months), these files can be permanently deleted.

**Deletion checklist** (after 90 days):
- [ ] Team is using `.work-items/` exclusively
- [ ] No references to old structure in active work
- [ ] Migration validation accepted by all stakeholders
- [ ] Archive created in git history (before deletion)

---

**For questions about migration**, see:
- `MIGRATION_COMPLETE.md` - Overview
- `MIGRATION_VALIDATION.md` - Detailed validation
- `.claude/migration.md` - Migration tracking

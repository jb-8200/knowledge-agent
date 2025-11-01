# ⚠️ DEPRECATED: tasks/ directory

This directory contains **legacy task files** and is **no longer the canonical source**.

## Migration Notice

All tasks have been reorganized into the **feature-based structure** under `.work-items/` following the **genai-specs workflow**.

### New Location

Tasks are now organized by feature in:
```
.work-items/
├── 01-project-setup/
├── 02-document-ingestion/
├── 03-vector-search-rag/
├── 04-external-search/
├── 05-answer-synthesis/
├── 06-web-ui/
├── 07-youtube-thumbnails/
├── 08-similar-questions/
├── 09-pin-answers/
├── 10-download-markdown/
├── 11-deployment/
├── 12-testing-feedback/
└── 13-spec-driven-integration/
```

### What Changed

**Old Structure** (Deprecated):
- `tasks/task_01.md` - Flat task list
- `specs/spec_01.md` - Separate specs
- `acceptance_tests/test_task_01.md` - Separate tests

**New Structure** (Current):
```
.work-items/{feature-name}/
├── user-story.md          # User-centric story (EARS format)
├── design.md              # Consolidated technical design
├── task.md                # TDD-focused task breakdown
├── 01_step_name.md        # Sequential implementation steps
├── 02_step_name.md
└── ...
```

### Task Mapping

| Old Task | New Feature | Location |
|----------|------------|----------|
| task_01-02 | F01: project-setup | .work-items/01-project-setup/ |
| task_03-07 | F02: document-ingestion | .work-items/02-document-ingestion/ |
| task_08-10 | F03: vector-search-rag | .work-items/03-vector-search-rag/ |
| task_11-13 | F04: external-search | .work-items/04-external-search/ |
| task_14-17 | F05: answer-synthesis | .work-items/05-answer-synthesis/ |
| task_18-20 | F06: web-ui | .work-items/06-web-ui/ |
| task_21 | F07: youtube-thumbnails | .work-items/07-youtube-thumbnails/ |
| task_22 | F08: similar-questions | .work-items/08-similar-questions/ |
| task_23 | F09: pin-answers | .work-items/09-pin-answers/ |
| task_24 | F10: download-markdown | .work-items/10-download-markdown/ |
| task_25-27 | F11: deployment | .work-items/11-deployment/ |
| task_28-30 | F12: testing-feedback | .work-items/12-testing-feedback/ |
| task_31-36 | F13: spec-driven-integration | .work-items/13-spec-driven-integration/ |

### Why the Change?

The new structure follows **genai-specs best practices**:
- ✅ **User-centric**: Starts with user stories, not technical tasks
- ✅ **Feature-based**: Related tasks grouped together
- ✅ **TDD-focused**: Test-driven development methodology
- ✅ **ACID steps**: Atomic, consistent, isolated, durable implementation
- ✅ **Consolidated**: Specs and tests integrated into feature docs

### Backward Compatibility

These legacy files are **preserved for reference** but should **not be modified**.

For new work, use `.work-items/` structure.

---

**Migration Date**: November 2025
**Migration Guide**: See `.claude/migration.md`

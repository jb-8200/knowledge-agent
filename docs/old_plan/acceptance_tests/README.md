# ⚠️ DEPRECATED: acceptance_tests/ directory

This directory contains **legacy acceptance test files** and is **no longer the canonical source**.

## Migration Notice

All acceptance criteria have been **integrated into feature documentation** under `.work-items/` following the **genai-specs workflow**.

### New Location

Acceptance criteria are now in:
```
.work-items/{feature-name}/
├── user-story.md       # User-facing acceptance criteria (EARS format)
├── task.md             # Technical acceptance criteria
└── {step}.md           # Step-specific verification criteria
```

### What Changed

**Old**: Separate test files for each task
**New**: Integrated into user stories and task steps

### Benefits

- **Closer to requirements**: Acceptance criteria with user stories
- **TDD-focused**: Tests defined before implementation
- **EARS format**: Structured WHEN/THEN/SHALL criteria
- **Verification checklists**: Each step has acceptance verification

### Example Migration

**Old** (`acceptance_tests/test_task_03.md`):
```
Test Steps:
1. Upload a PDF file
2. Verify it's stored
3. Check endpoint returns 200
```

**New** (`.work-items/02-document-ingestion/user-story.md`):
```
## Acceptance Criteria (EARS Format)

- WHEN I upload a PDF file THEN I SHALL see confirmation it was added
- WHEN I submit a web URL THEN I SHALL see the page content was indexed
```

**And** (`.work-items/02-document-ingestion/01_file_upload_endpoint.md`):
```
## Acceptance Criteria Verification

- [x] POST /upload/file endpoint accepts PDF/DOCX/Markdown
- [x] File MIME types are validated
- [x] Uploaded files trigger ingestion pipeline
- [x] Test test_file_upload_success passes
```

---

**Migration Date**: November 2025
**Migration Guide**: See `.claude/migration.md`

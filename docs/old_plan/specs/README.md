# ⚠️ DEPRECATED: specs/ directory

This directory contains **legacy specification files** and is **no longer the canonical source**.

## Migration Notice

All specifications have been **consolidated into design documents** under `.work-items/{feature}/design.md` following the **genai-specs workflow**.

### New Location

Technical designs are now in:
```
.work-items/{feature-name}/design.md
```

For example:
- `specs/spec_03.md` → `.work-items/02-document-ingestion/design.md`
- `specs/spec_08.md` → `.work-items/03-vector-search-rag/design.md`
- `specs/spec_14.md` → `.work-items/05-answer-synthesis/design.md`

### What Changed

**Old**: Each task had a separate spec file (36 files)
**New**: Related specs are consolidated into one design document per feature (13 files)

### Benefits

- **Less duplication**: Related technical details in one place
- **Better context**: See the full feature design at once
- **Clearer traceability**: Links user story → design → implementation
- **genai-specs compliant**: Follows industry best practices

### Spec Mapping

| Old Specs | New Design Document |
|-----------|-------------------|
| spec_01-02 | .work-items/01-project-setup/design.md |
| spec_03-07 | .work-items/02-document-ingestion/design.md |
| spec_08-10 | .work-items/03-vector-search-rag/design.md |
| spec_11-13 | .work-items/04-external-search/design.md |
| spec_14-17 | .work-items/05-answer-synthesis/design.md |
| spec_18-20 | .work-items/06-web-ui/design.md |
| spec_21 | .work-items/07-youtube-thumbnails/design.md |
| spec_22 | .work-items/08-similar-questions/design.md |
| spec_23 | .work-items/09-pin-answers/design.md |
| spec_24 | .work-items/10-download-markdown/design.md |
| spec_25-27 | .work-items/11-deployment/design.md |
| spec_28-30 | .work-items/12-testing-feedback/design.md |
| spec_31-36 | .work-items/13-spec-driven-integration/design.md |

---

**Migration Date**: November 2025
**Migration Guide**: See `.claude/migration.md`

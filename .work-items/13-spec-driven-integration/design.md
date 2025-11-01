# Design: Spec-Driven Integration

## Objective
Configure genai-specs workflow for Claude Code development.

## Status
✅ **COMPLETED** - This feature was implemented during migration setup:

- ✅ rules/ directory with all genai-specs files
- ✅ .claude/settings.json configured
- ✅ .claude/hooks/ with pre_prompt, pre_patch, pre_commit
- ✅ scripts/claude-init.sh bootstrap script
- ✅ .vale.ini and .markdownlint-cli2.yaml
- ✅ evals/golden-queries.yaml exists

## Remaining Work
- Create additional golden queries for evaluation
- Document hook usage
- Add CI integration for linting

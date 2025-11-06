 
# Knowledge Agent - Session Context

**Last Updated**: November 1, 2025
**Status**: Migration complete, ready for development

## 🎯 Project Overview

A **knowledge-base agent** using **RAG (truth) + CAG (intelligence)** built with:
- **LangChain** (agent framework) + **Firecrawl** (web extraction) + **Qdrant** (vector store)
- **FastAPI** backend, HTML/CSS/JS frontend
- Document ingestion (PDF, Word, Markdown, URLs) → Vector search → Web search → Citation

**Quick Navigation**:
- 📋 PROJECT_STRUCTURE.md - Complete project layout
- ⭐ docs/architecture.md - RAG + CAG system design
- 📂 .work-items/ - CANONICAL SOURCE (13 features, 53+ files)
- 🗄️ old_plan/ - Archived (DO NOT EDIT)

## 📂 Directory Map

```
.work-items/        # Feature-based work items (CANONICAL)
  ├── 01-project-setup/         # P0: Tasks 01-02
  ├── 02-document-ingestion/    # P0: Tasks 03-07
  ├── 03-vector-search-rag/     # P0: Tasks 08-10
  ├── 05-answer-synthesis/      # P0: Tasks 14-17 (RAG+CAG)
  ├── 04-external-search/       # P1: Tasks 11-13
  ├── 06-web-ui/                # P1: Tasks 18-20
  └── 07-10, 11, 12, 13/        # P1-P2: UI features, deploy, testing

.claude/plans/      # Active work tracking (symlinks to task.md files)
rules/              # genai-specs (auto-loaded by hooks)
docs/               # architecture.md (MAIN), scope.md, features.md, migration/
scripts/            # claude-init.sh, copy-genai-specs.sh, start-feature.sh, complete-feature.sh
old_plan/           # Archived 36 tasks/specs/tests (reference only)
```

## Core Principles (Always Apply)

1. **Evidence-Based Engineering** - Never make claims without measurement or citations
2. **Small Batch Sizes** - Most critical delivery principle
3. **TDD Mandatory** - Red → Green → Refactor cycle
4. **Tidy First** - Never mix structural and behavioral changes in same commit
5. **User-Centric** - Everything driven by user value
6. **RAG for truth** - Internal corpus is source of truth
7. **CAG for intelligence** - External search supplements gaps

## The Spec-Driven Workflow (Sequential Phases)

User Story → Design → Tasks → Implementation (TDD) → Verification

  1. User Story Phase (@./rules/standards-user-story.mdc)
  - Defines WHAT users want (non-technical, observable outcomes)
  - Format: "As a {persona}, I want to {action}, so that {value}"
  - Uses EARS format: WHEN/IF/WHILE... THEN... SHALL...
  - Stored: .work-items/{feature_name}/user-story.md
  - ❌ NO technical details (those go in design)

  2. Design Phase (@./rules/standards-design.mdc)
  - Defines HOW technically (components, APIs, data models)
  - Includes: Objective, Technical Design, Key Changes, Alternatives, Out of Scope
  - Stored: .work-items/{feature_name}/design.md
  - Must reference architecture decisions

  3. Task Breakdown (@./rules/standards-task.mdc)
  - Granular, technical work items (1-4 hours each)
  - Sequential ACID-compliant steps: 01_step.md, 02_step.md
  - Each task: actionable by code, independently testable, follows TDD
  - Stored: .work-items/{feature_name}/task.md + step files
  - ❌ Only mark complete when ALL acceptance criteria verified

  4. Implementation (TDD - @./rules/process-03-development.mdc)
  - Write failing test first (Red)
  - Minimal code to pass (Green)
  - Refactor (still Green)
  - Commit only when all tests pass
  - Separate structural commits from behavioral commits

  5. Verification (@./rules/guidelines-verification-protocol.mdc)
  - Run tests, linters, validation
  - Verify acceptance criteria

## 🔧 Technology Stack

**Backend**: FastAPI + LangChain + Qdrant + Firecrawl + Sentence Transformers
**Frontend**: HTML/CSS/JS (white theme, Google Search style)
**Deployment**: Firebase Hosting + Functions/Cloud Run or AWS ECS
**Environment**: `.env` for MODEL_PROVIDER_API_KEY, QDRANT_URL, SEARCH_API_KEY, YOUTUBE_API_KEY

## 🏗️ Architecture Pattern

```
User Query → RAG Retriever (Qdrant) → Synthesizer (decides if external needed)
                                            ↓
                          Web Search → Firecrawl → Summarizer
                                            ↓
                          Critic (merge internal + external) → Answer + Citations
```

## 📊 Progress Monitoring (genai-specs Pattern)

**Pattern**: Symlinks in `.claude/plans/` track active work (adapted from genai-specs Cursor Plans)

**Quick Commands**:
```bash
./scripts/start-feature.sh 01-project-setup      # Start work
ls .claude/plans/                                 # Check active work
./scripts/complete-feature.sh 01-project-setup   # Mark complete (verifies criteria)
```

**Key Principle**: Symlink presence = active, absence = complete/not started

**📖 Full Documentation**: See `.claude/plans/README.md` for:
- Detailed lifecycle management
- Verification requirements before completion
- Manual symlink commands
- Integration with development workflow
- Troubleshooting and examples

## 🤖 Custom Slash Commands & Skills

**Commands** (`.claude/commands/`):
```bash
/start-feature {name}     # Start a feature (creates symlink, shows task overview)
/next-step                # Show current step with TDD guidance
/verify-step              # Check acceptance criteria for current step
/complete-feature {name}  # Verify all criteria and complete feature
/test-rag [query]         # Test RAG pipeline end-to-end
/ingest {file|url}        # Quick document ingestion for testing
```

**Skills** (`.claude/skills/`):
- `tdd-workflow` - TDD cycle guidance, testing best practices, pytest usage
- `genai-specs` - Work items structure, EARS format, ACID tasks, verification protocol
- `rag-architecture` - RAG/CAG patterns, embeddings, vector search, Firecrawl integration

**Usage Notes**:
- Commands automate workflow steps (symlink management, verification, testing)
- Skills provide specialized knowledge loaded as context
- Commands integrate with `.work-items/` and `.claude/plans/` structure
- Use commands for execution, skills for understanding

## How I Should Work

**✅ DO**:
- Start with user stories, then design, then tasks
- Follow TDD religiously (Red → Green → Refactor)
- Keep commits small and atomic
- Separate structural (rename, refactor) from behavioral (new feature) commits
- Store work items in `.work-items/{feature_name}/` structure
- Verify acceptance criteria before marking tasks complete
- Cite sources and measure before making claims
- Reference `old_plan/` only for historical context (DO NOT EDIT)

**❌ DON'T**:
- Mix structural and behavioral changes in one commit
- Make technical claims without evidence
- Mark tasks complete before verification
- Include implementation details in user stories
- Commit when tests are failing
- Edit or create files in `old_plan/` (archived, read-only)

## 🚀 Development Start

**Next Steps**:
1. Run `./scripts/claude-init.sh` to verify setup
2. Start with `.work-items/01-project-setup/`
3. Follow P0 features: F01 → F02 → F03 → F05
4. Apply TDD for every task

**Session Checklist**:
- [ ] Review PROJECT_STRUCTURE.md for navigation
- [ ] Check docs/architecture.md for system design
- [ ] Browse .work-items/ for current feature
- [ ] Verify rules/ auto-loaded via pre_prompt hook
- [ ] Confirm TDD cycle: Red → Green → Refactor

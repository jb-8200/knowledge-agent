# Knowledge Agent - Project Structure

**Last Updated**: November 1, 2025 (deduplicated documentation)
**Status**: Ready for development

## Directory Structure

```
knowledge-agent/
├── .work-items/              # 📋 Feature-based work items (CANONICAL SOURCE)
│   ├── 01-project-setup/
│   ├── 02-document-ingestion/
│   ├── 03-vector-search-rag/
│   ├── 04-external-search/
│   ├── 05-answer-synthesis/
│   ├── 06-web-ui/
│   ├── 07-youtube-thumbnails/
│   ├── 08-similar-questions/
│   ├── 09-pin-answers/
│   ├── 10-download-markdown/
│   ├── 11-deployment/
│   ├── 12-testing-feedback/
│   └── 13-spec-driven-integration/
│
├── rules/                    # 📚 genai-specs process & standards
│   ├── process-*.mdc        # Core development process
│   ├── standards-*.mdc      # Documentation standards
│   └── guidelines-*.mdc     # Technology-specific guidelines
│
├── .claude/                  # ⚙️ Claude Code configuration
│   ├── DEVELOPMENT.md       # Development instructions (auto-loaded)
│   ├── settings.json        # Project settings
│   ├── settings.local.json  # Local permissions
│   ├── plans/               # 📊 Active work tracking (symlinks)
│   │   └── README.md        # Progress monitoring guide
│   └── hooks/               # Pre-commit, pre-patch, pre-prompt hooks
│
├── docs/                     # 📖 Project documentation
│   ├── README.md            # Documentation index
│   ├── architecture.md      # ⭐ System architecture (MAIN DOC)
│   ├── scope.md             # Project scope & phases
│   ├── features.md          # Feature catalog
│   ├── migration/           # Migration records (Nov 2025)
│   │   ├── README.md
│   │   ├── MIGRATION_COMPLETE.md
│   │   ├── MIGRATION_VALIDATION.md
│   │   ├── ARCHIVAL_COMPLETE.md
│   │   └── migration.md
│   └── decisions/           # Architecture Decision Records (ADRs)
│       └── README.md
│
├── scripts/                  # 🔧 Utility scripts
│   ├── claude-init.sh       # Bootstrap Claude Code session
│   └── copy-genai-specs.sh  # Update genai-specs files
│
├── evals/                    # ✅ Evaluation & testing
│   └── golden-queries.yaml  # Golden query dataset
│
├── old_plan/                 # 📦 Archived (reference only)
│   ├── tasks/               # Original 36 task files
│   ├── specs/               # Original 36 spec files
│   └── acceptance_tests/    # Original 36 test files
│
├── observability/            # 📊 Monitoring & logging
│   └── README.md
│
├── .vale.ini                 # Prose linting config
├── .markdownlint-cli2.yaml  # Markdown linting config
└── PROJECT_STRUCTURE.md      # This file (navigation guide)
```

## Key Directories Explained

### 📋 `.work-items/` (Most Important)

**Purpose**: Feature-based work items following genai-specs workflow

**Structure**:
```
{feature-name}/
├── user-story.md       # User persona, EARS format acceptance criteria
├── design.md           # Consolidated technical design
├── task.md             # TDD-focused task breakdown
└── NN_step.md          # Sequential implementation steps
```

**Usage**: This is the **canonical source** for all development work.

---

### 📚 `rules/`

**Purpose**: genai-specs process, standards, and technology guidelines

**Contents**:
- **process-*.mdc**: Core development process (TDD, Tidy First, etc.)
- **standards-*.mdc**: Documentation standards (user stories, designs, tasks)
- **guidelines-*.mdc**: Technology-specific guidelines (Python, TypeScript, etc.)

**Usage**: Auto-loaded by Claude Code via hooks. Reference with `@./rules/filename.mdc`

---

### ⚙️ `.claude/`

**Purpose**: Claude Code configuration, hooks, and progress monitoring

**Contents**:
- `DEVELOPMENT.md`: Development instructions (auto-loaded at session start)
- `settings.json`: Project settings, hook configuration
- `settings.local.json`: Local permission overrides
- `plans/`: Active work tracking using symlinks (adapted from genai-specs Cursor Plans)
- `hooks/`: Python hooks (pre_prompt, pre_patch, pre_commit)

**Usage**:
- Automatically loads development instructions, genai-specs rules, runs linters, executes tests
- Track active features via symlinks in `plans/` directory
- Check progress: `ls .claude/plans/` shows currently active work

---

### 📖 `docs/`

**Purpose**: Project documentation and historical records

**Structure**:
- **`architecture.md`** ⭐ - Main system architecture document (RAG + CAG)
- **`scope.md`** - Project scope and 10 development phases
- **`features.md`** - Feature catalog and capabilities
- `migration/` - Complete migration documentation (Nov 2025)
- `decisions/` - Architecture Decision Records (ADRs) - future use

**Usage**: Start with `architecture.md` for system overview, then dive into `.work-items/` for implementation details

---

### 🔧 `scripts/`

**Purpose**: Utility scripts for project management

**Key Scripts**:
- `claude-init.sh`: Bootstrap Claude Code session, verify setup
- `copy-genai-specs.sh`: Update genai-specs files from GitHub

---

### 📦 `old_plan/`

**Purpose**: Archived original planning files (reference only)

**Contents**: Original 36 tasks, 36 specs, 36 acceptance tests

**Usage**: Reference only, DO NOT edit. Use `.work-items/` for current work.

---

## File Types

### Root-Level Files

| File | Purpose |
|------|---------|
| `PROJECT_STRUCTURE.md` | This file - project structure guide |
| `.vale.ini` | Prose linting configuration |
| `.markdownlint-cli2.yaml` | Markdown linting rules |

### Key Documentation (in `docs/`)

| File | Purpose |
|------|---------|
| `docs/architecture.md` ⭐ | Main system architecture (RAG + CAG) |
| `docs/scope.md` | Project scope, phases, overview |
| `docs/features.md` | Feature catalog with capabilities |

### Configuration Files

| File | Purpose |
|------|---------|
| `.vale.ini` | Prose linting configuration (Vale) |
| `.markdownlint-cli2.yaml` | Markdown linting rules |

---

## Workflow

### For Development

1. **Browse features**: `ls .work-items/`
2. **Pick a feature**: `cd .work-items/01-project-setup`
3. **Read documentation**:
   - `user-story.md` - Understand user value
   - `design.md` - Review technical approach
   - `task.md` - See task breakdown
4. **Follow steps**: `01_init_repo.md`, `02_create_env.md`, etc.
5. **Use TDD**: Red → Green → Refactor

### For Documentation

- **User stories**: Follow `rules/standards-user-story.mdc`
- **Designs**: Follow `rules/standards-design.mdc`
- **Tasks**: Follow `rules/standards-task.mdc`
- **ADRs**: Follow `rules/standards-decision.mdc`

### For Claude Code

```bash
./scripts/claude-init.sh  # Verify setup
# DEVELOPMENT.md + genai-specs rules auto-load via .claude/hooks/pre_prompt.py
# Can also reference explicitly: @./.claude/DEVELOPMENT.md
```

### For Progress Monitoring

**Pattern**: Symlink-based active work tracking (genai-specs Cursor Plans)

**Quick commands**:
- Start: `./scripts/start-feature.sh <feature-name>`
- Check: `ls .claude/plans/`
- Complete: `./scripts/complete-feature.sh <feature-name>`

**Full documentation**: See `.claude/plans/README.md` for:
- Complete lifecycle management
- Time tracking workflow
- Verification requirements
- Manual commands and examples

---

## Feature Priority

**P0 (Critical) - Start here**:
- F01: project-setup
- F02: document-ingestion
- F03: vector-search-rag
- F05: answer-synthesis

**P1 (Important)**:
- F04: external-search
- F06: web-ui
- F11: deployment
- F12: testing-feedback

**P2 (Enhancement)**:
- F07-F10: UI features

---

## Quick Start Reading Order

1. **`PROJECT_STRUCTURE.md`** (this file) - Understand project layout
2. **`docs/architecture.md`** ⭐ - Learn system architecture
3. **`docs/scope.md`** - Review phases and scope
4. **`.work-items/01-project-setup/`** - Start implementing

## Related Documentation

- **Architecture**: `docs/architecture.md` ⭐
- **Migration docs**: `docs/migration/README.md`
- **Rules index**: `rules/` directory
- **Work items**: `.work-items/` directory (CANONICAL SOURCE)
- **Archive**: `old_plan/README.md`

---

**For questions or updates, see `docs/README.md`**

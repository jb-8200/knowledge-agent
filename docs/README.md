# Project Documentation

This directory contains project-level documentation including architecture, decisions, and historical records.

## Directory Structure

```
docs/
├── README.md           # This file
├── architecture.md     # ⭐ System architecture (RAG + CAG)
├── scope.md            # Project scope & phases
├── features.md         # Feature catalog
├── migration/          # Migration to genai-specs workflow (Nov 2025)
└── decisions/          # Architecture Decision Records (ADRs) [future]
```

## 🏗️ Architecture Documentation (Start Here!)

### **architecture.md** ⭐ MAIN ARCHITECTURE DOCUMENT

Complete system architecture including:
- Overall RAG (Retrieval-Augmented Generation) + CAG (Contextual-Augmented Generation) design
- Component structure with mermaid diagrams
- Workflow sequences
- Design decisions and justifications
- Technology stack (LangChain, Firecrawl, Qdrant, FastAPI)

**Read this first** to understand the system architecture.

### **scope.md** - Project Scope & Phases

High-level overview of the project organized by phases:
- 10 development phases (Setup → Testing → Spec-driven integration)
- Phase descriptions
- Original task breakdown by phase

**Note**: For current implementation details, see `.work-items/` (canonical source).

### **features.md** - Feature Catalog

Quick reference of all system features:
- Feature descriptions
- Capability overview
- Maps features to original task numbers

**Note**: For detailed feature specs, see `.work-items/{feature-name}/` (canonical source).

---

## 📦 Migration Documentation

See **`migration/`** directory for complete records of the migration from flat task/spec structure to genai-specs feature-based workflow (November 2025).

Key documents:
- **MIGRATION_COMPLETE.md** - Migration overview and summary
- **MIGRATION_VALIDATION.md** - Detailed validation showing all 36 tasks migrated
- **ARCHIVAL_COMPLETE.md** - Archival of old directories to `old_plan/`
- **migration.md** - Detailed migration tracking and feature mapping

## Work Items (Canonical Source)

For current development work, see **`../.work-items/`** - this is the canonical source for:
- User stories
- Technical designs
- Task breakdowns
- Implementation steps

## Architecture Decisions (Future)

Architecture Decision Records (ADRs) will be stored in `decisions/` as they are created during development.

Format: `NNNN-title-of-decision.md` (e.g., `0001-use-qdrant-for-vector-store.md`)

## Other Documentation

- **Development Instructions**: `../.claude/DEVELOPMENT.md` - Session context and genai-specs workflow (auto-loaded)
- **Rules**: `../rules/` - genai-specs process and standards
- **Evaluation**: `../evals/` - Golden queries for testing
- **Scripts**: `../scripts/` - Bootstrap and utility scripts
- **Project Structure**: `../PROJECT_STRUCTURE.md` - Complete navigation guide

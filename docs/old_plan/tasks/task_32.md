# Task 32 – Set up work‑item YAML definitions

**Phase:** Spec‑Driven Integration

**Description:**

Create a `.work-items/` directory at the project root.  Each YAML file
in this directory represents a small unit of work that Claude Code can
execute.  Define the schema for work items (`id`, `user_story`,
`spec_refs`, `acceptance_tests`, `code_targets` and `description`).
Add at least one example work item (e.g., `001_bootstrap_spec.yaml`)
mapping a user story to relevant spec sections and code targets.

**Acceptance Criteria:**

* The `.work-items/` directory exists in the repository.
* A YAML schema definition or example is provided documenting the
  required keys for a work item.
* At least one work item YAML file (`001_bootstrap_spec.yaml`) is
  present and contains meaningful references to specs and tasks.
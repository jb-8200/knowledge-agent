# Task 31 – Import genai‑specs and create rules directory

**Phase:** Spec‑Driven Integration

**Description:**

Add the `genai‑specs` repository as a Git submodule under the project
root.  Copy or symlink the always‑included specification files
(`process-01..05.mdc`, `standards-design.mdc`, `standards-task.mdc`,
`standards-architecture.mdc`, `standards-decision.mdc`) into a new
`rules/` directory.  Document the purpose of this directory and how
these files are used to provide context to Claude Code.  The submodule
should track a specific commit to ensure reproducibility.

**Acceptance Criteria:**

* The repository contains a `genai-specs` submodule configured in
  `.gitmodules` and initialised locally.
* A `rules/` directory exists with copies or symbolic links of the
  always‑included specification files.
* The README in `rules/` explains how to update the files when the
  submodule is updated and how they are loaded by Claude Code.
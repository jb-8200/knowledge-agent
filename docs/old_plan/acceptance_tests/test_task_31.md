# Test Task 31 – Import genai‑specs and create rules directory

## Objective

Verify that the repository has been prepared for spec‑driven development by
adding the `genai‑specs` submodule and copying the always‑included
specifications into a `rules/` directory.

## Steps

1. Inspect the `.gitmodules` file to ensure that a `genai-specs`
   submodule is defined and points to
   `https://github.com/betsalel-williamson/genai-specs`.
2. Confirm that a directory named `genai-specs/` exists at the root of
   the project and contains specification files (e.g., `process-01.mdc`).
3. Confirm that a `rules/` directory exists in the project root and
   contains symlinks or copies of the following files:
   - `process-01.mdc` through `process-05.mdc`
   - `standards-design.mdc`
   - `standards-task.mdc`
   - `standards-architecture.mdc`
   - `standards-decision.mdc`
4. Open `rules/README.md` and verify that it explains how these files
   are used by Claude Code and how to update them.

## Expected Outcome

* The submodule is correctly registered, the `genai-specs/` directory
  exists and the core specification files are available in `rules/`.
* The `rules/README.md` clearly documents how to refresh the files
  when updating the submodule and how they are loaded during
  development.
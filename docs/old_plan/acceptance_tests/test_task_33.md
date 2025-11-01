# Test Task 33 – Write a bootstrap script for Claude Code

## Objective

Ensure that the `claude-init.sh` script exists, is executable, and
performs the bootstrap checks and prompt generation correctly.

## Steps

1. Verify that the file `scripts/claude-init.sh` exists and has
   executable permissions (`rwx` for the owner).
2. With the `genai-specs` submodule present, run `./scripts/claude-init.sh`
   from the project root and capture the output.
3. Confirm that the script does not produce any error messages and
   prints a prompt listing each of the core rule files (e.g.,
   `@./rules/process-01.mdc`, `@./rules/standards-decision.mdc`).
4. Delete or rename the `.env` file, rerun the script and check that
   a new `.env` file is created with default variables.

## Expected Outcome

* The script exists and is executable.
* When run in a repository with the `genai-specs` submodule, the
  script prints a kickoff prompt containing include lines for all
  rules files and does not error.
* If `.env` is missing, the script creates a minimal `.env` file
  containing keys such as `LLM_PROVIDER` and `QDRANT_URL`.
* When the submodule is absent, the script outputs an error
  instructing the developer to add the submodule.
# Task 33 – Write a bootstrap script for Claude Code

**Phase:** Spec‑Driven Integration

**Description:**

Implement a shell script (`scripts/claude-init.sh`) that performs the
initial setup for a Claude Code session.  The script should:

1. Verify that the `genai‑specs` submodule is present; if not,
   instruct the developer to add it.
2. Ensure the `rules/` directory exists and prompt the developer to
   copy or link the specification files into it.
3. Create a minimal `.env` file with placeholder variables for
   local LLM and infrastructure configuration if one does not exist.
4. Print a kickoff prompt that instructs Claude Code to load the
   core rules from the `rules/` directory.

**Acceptance Criteria:**

* The `scripts/claude-init.sh` file exists and is executable (`chmod
  +x`).
* Running the script without a submodule displays an error and
  instructions for adding it.
* Running the script with the submodule prints a prompt listing the
  rules files and leaves the repository unchanged.
* The script generates `.env` if missing but does not overwrite
  existing environment files.
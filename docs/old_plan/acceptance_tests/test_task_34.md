# Test Task 34 – Configure spec hygiene tooling

## Objective

Verify that linting tools for markdown documentation are configured
properly and usable by developers.

## Steps

1. Confirm that `.vale.ini` and `.markdownlint-cli2.yaml` exist at the
   root of the repository and contain non‑empty configurations.
2. Install `vale` and `markdownlint-cli2` (if not already installed)
   according to the developer documentation.
3. Run `vale` against a sample markdown file (e.g., `README.md` or
   `high_level_design.md`) and ensure that the tool completes
   without crashing.  Warnings or suggestions are acceptable; no
   critical errors should occur.
4. Run `markdownlint` against the same file and verify that it
   completes successfully.

## Expected Outcome

* Both configuration files exist and are valid.
* The linting tools run without fatal errors on existing markdown
  documents, providing feedback on formatting and style.
* The developer documentation describes how to install and execute
  these tools locally.
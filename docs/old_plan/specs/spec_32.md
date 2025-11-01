# Spec 32 – Set up work‑item YAML definitions

This specification explains how to create a `.work-items/` directory and define
YAML cards that drive spec‑driven development.  Work items break down
requirements into small, traceable units that link user stories to
specifications, acceptance tests and code targets.  They do not replace the
existing task and spec documents; rather, they provide additional metadata
that Claude Code can consume to automate patch generation.

## Steps

1. **Create the directory.**  At the root of the repository, create a
   directory named `.work-items/`.  This directory should be committed to
   version control.  Each file in this folder will be a YAML document
   describing a single work item.

2. **Define the schema.**  Each work‑item YAML file must contain the
   following keys:

   - `id`: A unique identifier for the work item (e.g., `001`).
   - `user_story`: A one‑sentence description of the user outcome or
     functionality being addressed.
   - `description`: A brief summary of the technical change or feature.
   - `spec_refs`: A list of specification documents that this work item
     implements.  Use the form `spec_XX` to reference the spec file.
   - `acceptance_tests`: A list of acceptance test files that verify the
     implementation (e.g., `test_task_01.md`).
   - `code_targets`: A list of files or modules in the codebase that will be
     created or modified.

3. **Provide an example.**  Add an example work item such as
   `001_bootstrap_spec.yaml` with the following content:

   ```yaml
   id: 001
   user_story: "As a developer, I want Claude Code to load our process rules automatically."
   description: "Bootstrap Claude Code by verifying the genai‑specs submodule and loading core rules."
   spec_refs:
     - spec_31
   acceptance_tests:
     - test_task_31.md
   code_targets:
     - scripts/claude-init.sh
     - rules/
   ```

4. **Use work items in prompts.**  When starting a coding session, provide
   the relevant work‑item YAML to Claude Code using the `@` syntax or by
   copying its contents into the prompt.  This ensures that Claude has
   access to the user story, spec references and test files.

## Notes

* Work items are meant for development workflow automation; they do not
  change the existing architectural design.  Each YAML file should remain
  concise and machine‑readable.
* Additional fields may be added as needed (e.g., `depends_on` to express
  ordering), but they must be documented in the repository’s developer
  guidelines.
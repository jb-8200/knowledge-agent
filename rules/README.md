# Rules Directory

This directory is reserved for importing the core process and standards files from the
`genai-specs` submodule.  When you clone this repository for local development you
should run `git submodule update --init` to bring in the `genai-specs` repo and then
symlink or copy the following files into this folder:

- `process-01.mdc` through `process-05.mdc`
- `standards-design.mdc`
- `standards-task.mdc`
- `standards-architecture.mdc`
- `standards-decision.mdc`

These files are referenced by the bootstrap script (`scripts/claude-init.sh`) to
seed Claude Code with consistent context for every session.

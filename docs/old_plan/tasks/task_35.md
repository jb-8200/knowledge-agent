# Task 35 – Implement Claude Code hooks

**Phase:** Spec‑Driven Integration

**Description:**

Create a `.claude/hooks/` directory and implement Python scripts for
pre‑prompt, pre‑patch and pre‑commit hooks.  The pre‑prompt hook
should prepend includes of the core rules to each prompt unless they
are already present.  The pre‑patch hook should run Vale and
Markdownlint on changed Markdown files and insert any lint messages
into the patch as HTML comments.  The pre‑commit hook should run
`pytest` to ensure unit tests pass before commits are created.  In
addition to the scripts, create a `.claude/settings.json` file that
registers these hooks under the appropriate events (`UserPromptSubmit`
and `PreToolUse`) with suitable matchers.  These hooks automate
quality checks and context loading for Claude Code.

**Acceptance Criteria:**

* The directory `.claude/hooks/` exists and contains three Python
  files: `pre_prompt.py`, `pre_patch.py` and `pre_commit.py`.
* The `pre_prompt_hook` function prepends includes for all rule
  files if they are not already present in the prompt.
* The `pre_patch_hook` function runs Vale and Markdownlint on
  Markdown files and inserts lint messages as comments into the diff.
* The `pre_commit_hook` runs the test suite via `pytest` and aborts
  the commit if tests fail.
* A `.claude/settings.json` file exists and registers the hooks
  according to the specification; it uses the `UserPromptSubmit` event
  for the pre‑prompt hook and `PreToolUse` with the `Edit|MultiEdit|Write`
  matcher for the pre‑patch hook and the `Bash` matcher for the
  pre‑commit hook.
* Documentation exists explaining how these hooks are activated by
  Claude Code.
# Test Task 35 – Implement Claude Code hooks

## Objective

Ensure that custom Claude Code hooks are implemented and registered
correctly, providing automatic context loading, linting and test
execution.

## Steps

1. Check that the directory `.claude/hooks/` exists and contains
   three files: `pre_prompt.py`, `pre_patch.py` and `pre_commit.py`.
2. Open each Python file and verify that it defines a hook function
   with the correct signature:
   - `pre_prompt_hook(prompt: str, context: dict) -> str`
   - `pre_patch_hook(files: list, diff: str, context: dict) -> str`
   - `pre_commit_hook(context: dict) -> str`
3. Inspect the body of each function to confirm that it performs the
   following tasks:
   - `pre_prompt_hook` prepends include lines for all rule files if
     they are missing.
   - `pre_patch_hook` runs Vale and Markdownlint on markdown files and
     adds any lint messages as HTML comments at the top of the diff.
   - `pre_commit_hook` runs `pytest` and returns a message only if tests
     fail.
4. Verify the presence of `.claude/settings.json` and that it
   registers the hooks under the `UserPromptSubmit` and `PreToolUse`
   events with appropriate matchers, matching the specification
   example.
5. Optionally, test the hooks by running a simulated Claude Code
   session and observing that prompts include the rules automatically
   and that committing with failing tests aborts the commit.

## Expected Outcome

* All three hook files and the settings configuration file exist and
  contain the expected function definitions and logic.
* The settings JSON file registers the hooks correctly, using the
  `UserPromptSubmit` event for the pre‑prompt hook and `PreToolUse`
  with appropriate matchers for the other hooks.
* Running Claude Code with these hooks results in automatic context
  inclusion, markdown linting feedback in patches, and test checks on
  commits.
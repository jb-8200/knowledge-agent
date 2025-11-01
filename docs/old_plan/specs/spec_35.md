# Spec 35 – Implement Claude Code hooks

This specification outlines how to create custom hooks for Claude
Code.  Hooks are scripts that run at specific lifecycle events
within a Claude Code session, allowing you to enforce rules and
perform automated checks.  According to best practices, project
hooks should reside in `.claude/hooks/` and be registered in
`.claude/settings.json`【795882351538242†L17-L29】.

## Steps

1. **Create the hooks directory.**  In the project root, create a
   hidden directory `.claude/hooks/` if it does not already exist.
   This directory will hold your hook scripts.  Organizing hooks in
   their own directory avoids embedding complex logic directly in
   JSON configuration【795882351538242†L42-L48】.

2. **Write the pre‑prompt hook.**  Create a Python file
   `.claude/hooks/pre_prompt.py` with a function
   `pre_prompt_hook(prompt: str, context: dict) -> str`.  This
   function should check whether the current prompt already includes
   the project rules (via the `@./rules/` includes).  If not, it
   prepends a header with include lines for each rules file:

   ```python
   def pre_prompt_hook(prompt: str, context: dict) -> str:
       include_lines = [
           "@./rules/process-01.mdc",
           "@./rules/process-02.mdc",
           "@./rules/process-03.mdc",
           "@./rules/process-04.mdc",
           "@./rules/process-05.mdc",
           "@./rules/standards-design.mdc",
           "@./rules/standards-task.mdc",
           "@./rules/standards-architecture.mdc",
           "@./rules/standards-decision.mdc",
       ]
       if any(line in prompt for line in include_lines):
           return prompt
       header = "\n".join(include_lines) + "\n\n"
       return header + prompt
   ```

   This ensures that the core rules are always included at the
   beginning of each interaction with Claude.  Hook functions return
   the modified prompt string.

3. **Write the pre‑patch hook.**  Create a Python file
   `.claude/hooks/pre_patch.py` with two functions: `run_lint` and
   `pre_patch_hook`.  The hook should iterate over changed files
   (passed as a list) and, for each markdown or MDC file, run
   `vale` and `markdownlint` via `subprocess.run`.  Collect any
   output and prepend it to the patch as HTML comments.  For
   example:

   ```python
   import subprocess
   from pathlib import Path
   from typing import List

   def run_lint(file_paths: List[str]) -> str:
       messages = []
       for path in file_paths:
           p = Path(path)
           if p.suffix.lower() in {".md", ".mdc"}:
               result = subprocess.run(["vale", path], capture_output=True, text=True)
               if result.stdout:
                   messages.append(result.stdout)
               result2 = subprocess.run(["markdownlint", path], capture_output=True, text=True)
               if result2.stdout:
                   messages.append(result2.stdout)
       return "\n".join(messages)

   def pre_patch_hook(files: List[str], diff: str, context: dict) -> str:
       lint_output = run_lint(files)
       if lint_output:
           comment = "\n".join([f"<!-- {line} -->" for line in lint_output.splitlines()])
           return comment + "\n" + diff
       return diff
   ```

   This hook ensures that documentation quality issues are surfaced
   directly within the code patch, encouraging developers to fix
   them before commits are made.

4. **Write the pre‑commit hook.**  Create a Python file
   `.claude/hooks/pre_commit.py` containing a function
   `pre_commit_hook(context: dict) -> str`.  This function runs
   `pytest` using `subprocess.run` and returns an error message if
   tests fail:

   ```python
   import subprocess

   def pre_commit_hook(context: dict) -> str:
       result = subprocess.run(["pytest", "--quiet", "--disable-warnings", "--maxfail=1"],
                               capture_output=True, text=True)
       if result.returncode != 0:
           return "Tests failed:\n" + result.stdout + result.stderr + "\nCommit aborted."
       return ""
   ```

   If `pytest` is not installed, the hook may return a warning but
   should not abort the commit.

5. **Register the hooks.**  Create a `.claude/settings.json`
   configuration file and register the hooks under appropriate
   events.  Use the `PreToolUse` event with a matcher of
   `Edit|MultiEdit|Write` for the pre‑patch hook and a matcher of
   `Bash` for the pre‑commit hook.  Use the `UserPromptSubmit` event
   for the pre‑prompt hook.  The configuration should look like:

   ```json
   {
     "$schema": "https://json.schemastore.org/claude-code-settings.json",
     "hooks": {
       "UserPromptSubmit": [
         {
           "matcher": "*",
           "hooks": [
             {
               "type": "python",
               "path": ".claude/hooks/pre_prompt.py",
               "symbol": "pre_prompt_hook"
             }
           ]
         }
       ],
       "PreToolUse": [
         {
           "matcher": "Edit|MultiEdit|Write",
           "hooks": [
             {
               "type": "python",
               "path": ".claude/hooks/pre_patch.py",
               "symbol": "pre_patch_hook"
             }
           ]
         },
         {
           "matcher": "Bash",
           "hooks": [
             {
               "type": "python",
               "path": ".claude/hooks/pre_commit.py",
               "symbol": "pre_commit_hook"
             }
           ]
         }
       ]
     }
   }
   ```

   Registering the hooks in `.claude/settings.json` makes them part of
   the project configuration, ensuring every team member benefits from
   the same automation【795882351538242†L24-L29】.

## Notes

* Hooks run with your current credentials, so review hook code
  carefully and avoid executing untrusted commands【795882351538242†L149-L153】.
* Use the `/hooks` slash command in Claude Code to review and test
  your hooks configuration【795882351538242†L123-L128】.
* You may add additional hooks (e.g., `PostToolUse` debugging hooks) as
  needed to capture tool outputs during development.  The example in
  Aaron Brethorst’s article shows how to dump JSON output from file
  modifications【795882351538242†L110-L121】.
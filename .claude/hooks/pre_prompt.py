"""
Pre-prompt hook for Claude Code.

This hook ensures that Claude always has access to the core rules
before processing user input.  It inspects the current prompt and
prepends includes for the specification files if they are missing.
Claude Code calls this function before each user message.
"""

def pre_prompt_hook(prompt: str, context: dict) -> str:
    # Include project-specific development instructions and genai-specs rules.
    # DEVELOPMENT.md provides project context, tech stack, and workflow.
    # genai-specs rules provide core development standards.
    include_lines = [
        "@./.claude/DEVELOPMENT.md",
        "@./rules/process-01-core.mdc",
        "@./rules/process-02-project.mdc",
        "@./rules/process-03-development.mdc",
        "@./rules/process-04-operational.mdc",
        "@./rules/process-05-coding.mdc",
        "@./rules/standards-user-story.mdc",
        "@./rules/standards-design.mdc",
        "@./rules/standards-task.mdc",
        "@./rules/standards-architecture.mdc",
        "@./rules/standards-decision.mdc",
        "@./rules/standards-guidelines.mdc",
    ]
    if any(line in prompt for line in include_lines):
        # Context already loaded.
        return prompt
    header = "\n".join(include_lines) + "\n\n"
    return header + prompt

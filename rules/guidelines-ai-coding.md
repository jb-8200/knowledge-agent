# Guidelines: AI-Assisted Coding with Claude Code

**Audience**: ML Team Leaders, Software Architects
**Purpose**: Comprehensive guide to AI coding enhancement methods and developer productivity improvements
**Last Updated**: November 6, 2025

---

## Table of Contents

1. [Introduction](#introduction)
2. [Part 1: Theory & Concepts](#part-1-theory--concepts)
3. [Part 2: Project Implementation](#part-2-project-implementation)
4. [Part 3: Spec-Driven Development](#part-3-spec-driven-development)
5. [Part 4: Cursor vs Claude Code Benchmark](#part-4-cursor-vs-claude-code-benchmark)
6. [Conclusion & Recommendations](#conclusion--recommendations)

---

## Introduction

This guide explains the methods and approaches used in the knowledge-agent project to enhance AI code assistance and improve developer productivity through **Claude Code**, Anthropic's official CLI for Claude.

### What is Claude Code?

Claude Code is a terminal-based AI coding assistant that provides:
- **Full codebase context** (200k token window)
- **Extensible plugin system** (hooks, skills, commands, MCP)
- **Plan-first approach** (think before executing)
- **Transparent execution** (all actions visible in terminal)
- **Fine-grained control** (incremental permissions, tool-by-tool)

### Why This Matters

Modern AI-assisted development isn't just about autocomplete or chat. It's about:
1. **Enforcing standards** automatically (via hooks)
2. **Injecting specialized knowledge** (via skills)
3. **Automating workflows** (via commands)
4. **Maintaining rigor** (via spec-driven development)
5. **Maximizing productivity** while maintaining quality

This project demonstrates **best-in-class** use of these capabilities.

---

## Part 1: Theory & Concepts

Understanding the building blocks of Claude Code's extensibility system.

### 🪝 Hooks

**Definition**: Python scripts that execute at specific points in Claude's lifecycle to inject context, run validations, or enforce standards.

**Analogy**: Like Git hooks, but for AI interactions. They intercept and augment Claude's actions.

#### Hook Types

| Hook Type | When It Runs | Use Cases |
|-----------|--------------|-----------|
| **UserPromptSubmit** | Before processing user input | Auto-load project context, inject rules, transform prompts |
| **PreToolUse** | Before Claude executes any tool (Edit, Write, Bash, etc.) | Validate inputs, run linters, enforce permissions |
| **PostToolUse** | After a tool completes successfully | Verify outputs, trigger follow-up actions, logging |

#### Hook Structure

```python
# .claude/hooks/example_hook.py

def hook_function(context: dict, **kwargs) -> str:
    """
    Hook functions receive context and can return modifications.

    Args:
        context: Dict with session info, file paths, user input, etc.
        **kwargs: Additional parameters depending on hook type

    Returns:
        Modified string (e.g., updated prompt, error message, etc.)
    """
    # Your validation/transformation logic
    return result
```

**Configuration** (`.claude/settings.json`):
```json
{
  "hooks": {
    "userPromptSubmit": [{
      "matcher": "*",
      "hooks": [{
        "type": "python",
        "path": ".claude/hooks/pre_prompt.py",
        "symbol": "pre_prompt_hook"
      }]
    }]
  }
}
```

#### When to Use Hooks

✅ **Use hooks when**:
- Need automatic context injection (every session should load X)
- Want to enforce standards (linting, testing before commits)
- Need to validate inputs before tool execution
- Want to transform user prompts programmatically

❌ **Don't use hooks when**:
- Action is optional/on-demand (use commands instead)
- Need interactive user input (hooks are automatic)
- Logic is too complex (keep hooks simple and fast)

---

### 🎓 Skills

**Definition**: Markdown files that provide specialized knowledge/context to Claude, loaded on-demand based on task requirements.

**Analogy**: Like a specialized consultant you bring in when needed. Skills provide deep expertise in specific domains.

#### Skill Structure

```markdown
# Skill Title

## When to Activate
Describes scenarios where this skill should be loaded.

## Core Concepts
Deep explanation of domain knowledge.

## Best Practices
Patterns, anti-patterns, examples.

## Project-Specific Guidance
How to apply this knowledge in this codebase.
```

**File Location**: `.claude/skills/{skill-name}/skill.md`

**Optional Metadata** (YAML frontmatter):
```yaml
---
name: "TDD Workflow"
description: "Test-Driven Development expertise"
tags: ["testing", "tdd", "pytest"]
---
```

#### Skills vs Commands vs Hooks

| Feature | Skills | Commands | Hooks |
|---------|--------|----------|-------|
| **Type** | Passive knowledge | Active instructions | Automatic triggers |
| **Activation** | On-demand (when relevant) | User invokes | Lifecycle events |
| **Purpose** | Provide expertise | Automate workflows | Enforce standards |
| **Format** | Markdown (documentation) | Markdown (templates) | Python (code) |
| **Example** | "RAG architecture patterns" | "/start-feature" | Pre-commit testing |

#### When to Use Skills

✅ **Use skills when**:
- Need deep domain knowledge (e.g., RAG, TDD, security)
- Context is reusable across many tasks
- Want to teach Claude specialized patterns
- Need to reference standards/methodologies

❌ **Don't use skills when**:
- Need immediate action (use commands)
- Content is project-specific config (use hooks)
- Information is already in codebase (just reference files)

---

### 💬 Commands

**Definition**: Slash commands (templates) that automate workflows by expanding into detailed prompts when invoked.

**Analogy**: Like shell aliases or macros. Type `/shortcut` to trigger a complex workflow.

#### Command Types

**1. Simple Commands** (Static template)
```markdown
# /hello Command

Say hello and explain what I can do for you.

Available commands:
- /start-feature {name}
- /test-rag [query]
```

**2. Commands with Arguments** (Dynamic placeholders)
```markdown
# /start-feature Command

Start working on feature: {{feature-name}}

Steps:
1. Create symlink in .claude/plans/
2. Read .work-items/{{feature-name}}/user-story.md
3. Show acceptance criteria
```

**3. Commands with Bash** (Include executable steps)
```markdown
# /run-tests Command

Run the test suite and report results.

```bash
pytest tests/ -v --tb=short
```

Check test coverage with pytest.
```

#### Command Structure

**File Location**: `.claude/commands/{command-name}.md`

**Basic Format**:
```markdown
Brief description of what this command does.

## Usage

/command-name arg1 arg2

## What This Does

1. Step 1 explanation
2. Step 2 explanation
3. Step 3 explanation

## Steps

Detailed implementation steps with code examples

## Output Format

Show what the user should expect to see
```

#### When to Use Commands

✅ **Use commands when**:
- Workflow has multiple steps
- Need to guide user through a process
- Want to standardize how tasks are done
- Workflow is repeated frequently

❌ **Don't use commands when**:
- Task is one-time/unique (just do it directly)
- Workflow is too simple (not worth a command)
- Need automatic execution (use hooks)

---

### 🤖 Subagents

**Definition**: Specialized AI agents for specific tasks, available via the Task tool in Claude Code.

**Analogy**: Like hiring specialized contractors for specific jobs while you (main Claude) oversee the project.

#### Subagent Types

| Type | Specialization | Tools Available | When to Use |
|------|----------------|-----------------|-------------|
| **general-purpose** | Multi-step tasks, research, coding | All tools | Complex tasks requiring multiple capabilities |
| **Explore** | Fast codebase exploration | Glob, Grep, Read, all tools | Finding files/patterns, understanding structure |
| **Plan** | Task planning and breakdown | All tools | Breaking down complex features, creating plans |

#### Task Tool Usage

The Task tool delegates work to a subagent. Specify:
- `subagent_type`: Which specialist to use
- `description`: Short task summary
- `prompt`: Detailed instructions
- `model`: Optional (sonnet/opus/haiku)

**Example use case**:
```
User asks: "Find all authentication code in the codebase"

Main Claude invokes Task tool with:
- subagent_type: Explore
- prompt: Search for auth endpoints, JWT handling, session management
- model: haiku (fast for exploration)

Explore agent:
- Uses Glob to find *auth*.py files
- Uses Grep to search for "login", "jwt", "session"
- Uses Read to examine key files
- Returns summary to main Claude

Main Claude:
- Receives exploration results
- Synthesizes findings
- Presents to user
```

#### When to Use Subagents

✅ **Use Task tool when**:
- Need deep codebase exploration (use Explore)
- Breaking down complex features (use Plan)
- Delegating independent subtasks
- Want specialized processing

❌ **Don't use Task tool when**:
- Simple file read (use Read directly)
- Single operation (overhead not worth it)
- Need tight control over each step

---

### 🔌 MCP (Model Context Protocol)

**Definition**: A protocol that allows Claude Code to connect to external tools and data sources as both a client and server.

**Analogy**: Like REST APIs, but specifically designed for AI-human-computer interaction.

#### MCP Architecture

```
┌─────────────────────────────────────────────┐
│           Claude Code (MCP Client)          │
│  Can connect to multiple MCP servers        │
└─────────────────┬───────────────────────────┘
                  │
      ┌───────────┴───────────┐
      │                       │
      ▼                       ▼
┌─────────────┐         ┌─────────────┐
│ MCP Server  │         │ MCP Server  │
│ (Database)  │         │ (External   │
│             │         │  API)       │
└─────────────┘         └─────────────┘
```

#### MCP Capabilities

**As Client**: Claude Code can connect to:
- Database servers (PostgreSQL, MongoDB, etc.)
- External APIs (GitHub, Jira, Slack, etc.)
- Custom tools you build
- Community MCP servers

**As Server**: Claude Code can expose:
- Project-specific tools
- Custom commands
- Data sources

#### Configuration

Create `.mcp.json` in project root:
```json
{
  "mcpServers": {
    "postgres": {
      "command": "npx",
      "args": ["-y", "@anthropic-ai/mcp-server-postgres"],
      "env": {
        "DATABASE_URL": "postgresql://localhost/mydb"
      }
    },
    "github": {
      "command": "npx",
      "args": ["-y", "@anthropic-ai/mcp-server-github"],
      "env": {
        "GITHUB_TOKEN": "${GITHUB_TOKEN}"
      }
    }
  }
}
```

#### When to Use MCP

✅ **Use MCP when**:
- Need to access external data sources
- Want to integrate third-party services
- Building reusable tools for multiple projects
- Need standardized AI-tool interface

❌ **Don't use MCP when**:
- Simple file operations (use built-in tools)
- One-off scripts (just write them directly)
- Security/privacy concerns with external connections

**Note**: This project doesn't currently use MCP, but it's available for future integration.

---

### Decision Matrix: Which Tool to Use?

| Scenario | Recommended Tool | Rationale |
|----------|------------------|-----------|
| Auto-load project context every session | **Hook** (UserPromptSubmit) | Automatic, runs every time |
| Enforce linting before edits | **Hook** (PreToolUse on Edit) | Automatic validation |
| Run tests before commits | **Hook** (PreToolUse on Bash git) | Prevents broken commits |
| Provide RAG/TDD expertise | **Skill** | Reusable knowledge, on-demand |
| Start a feature workflow | **Command** (/start-feature) | Multi-step process, user-initiated |
| Quick document ingestion | **Command** (/ingest) | Repeatable, parameterized |
| Find all uses of a function | **Subagent** (Explore) | Complex search across codebase |
| Connect to GitHub API | **MCP** | External integration |

---

## Part 2: Project Implementation

How these concepts are applied in the knowledge-agent project.

### 🎯 Project Overview

The knowledge-agent is a **RAG (Retrieval-Augmented Generation) + CAG (Contextual-Augmented Generation)** system built with:
- **Backend**: FastAPI + LangChain + Qdrant + Firecrawl
- **Frontend**: HTML/CSS/JS (white theme, Google Search style)
- **Methodology**: genai-specs (spec-driven development)
- **Quality**: TDD (Test-Driven Development) enforced via hooks

**Development Philosophy**:
1. Specifications before implementation
2. Red → Green → Refactor (TDD mandatory)
3. Small batch sizes (ACID tasks)
4. Evidence-based engineering
5. Single source of truth (`.work-items/`)

---

### 🪝 Active Hooks in This Project

#### 1. UserPromptSubmit Hook (Pre-Prompt)

**File**: `.claude/hooks/pre_prompt.py`

**Purpose**: Auto-loads project context and genai-specs rules before every user message.

**What it does**:
```python
def pre_prompt_hook(prompt: str, context: dict) -> str:
    """Prepend includes if not already present."""

    include_lines = [
        "@./.claude/DEVELOPMENT.md",        # Session context
        "@./rules/process-01-core.mdc",     # Core principles
        "@./rules/process-02-project.mdc",  # Project management
        "@./rules/process-03-development.mdc",  # TDD, Tidy First
        "@./rules/process-04-operational.mdc",  # Deployment
        "@./rules/process-05-coding.mdc",   # Coding standards
        "@./rules/standards-user-story.mdc",    # User story format
        "@./rules/standards-design.mdc",    # Design doc format
        "@./rules/standards-task.mdc",      # Task breakdown
        "@./rules/standards-architecture.mdc",  # ADR format
        "@./rules/guidelines-*.mdc",        # Technology guides
    ]

    # Check if includes already present
    # If not, prepend them
    return modified_prompt
```

**Configuration** (`.claude/settings.json`):
```json
{
  "hooks": {
    "userPromptSubmit": [{
      "matcher": "*",
      "hooks": [{
        "type": "python",
        "path": ".claude/hooks/pre_prompt.py",
        "symbol": "pre_prompt_hook"
      }]
    }]
  }
}
```

**Benefits for Developers**:
- ✅ Never forget to include project context
- ✅ Consistent development standards every session
- ✅ No manual file references needed
- ✅ ~30 seconds saved per session startup

**CLI Usage**: Automatic (no command needed)

**Expected Outcome**: Every user message automatically includes 12+ rules files and DEVELOPMENT.md context.

---

#### 2. PreToolUse Hook (Pre-Patch for Documentation)

**File**: `.claude/hooks/pre_patch.py`

**Purpose**: Runs Vale (prose linter) and markdownlint before editing markdown files.

**What it does**:
```python
def pre_patch_hook(files: List[str], diff: str, context: dict) -> str:
    """Run linters on markdown files before editing."""

    errors = []

    for file in files:
        if file.endswith(('.md', '.mdc')):
            # Run Vale
            vale_result = subprocess.run(['vale', file], capture_output=True)
            if vale_result.returncode != 0:
                errors.append(f"Vale errors in {file}:\n{vale_result.stdout}")

            # Run markdownlint
            mdlint_result = subprocess.run(['markdownlint', file], capture_output=True)
            if mdlint_result.returncode != 0:
                errors.append(f"Markdown errors in {file}:\n{mdlint_result.stdout}")

    if errors:
        return "\n".join(errors)  # Shown to Claude as comments in diff

    return ""  # No errors, proceed
```

**Configuration**:
```json
{
  "hooks": {
    "preToolUse": [{
      "matcher": "Edit|MultiEdit|Write",
      "hooks": [{
        "type": "python",
        "path": ".claude/hooks/pre_patch.py",
        "symbol": "pre_patch_hook"
      }]
    }]
  }
}
```

**Benefits for Developers**:
- ✅ Documentation quality enforced automatically
- ✅ Catches formatting issues before they're committed
- ✅ Consistent style across all docs
- ✅ No manual linting needed

**CLI Usage**: Automatic (runs before Edit/Write on .md files)

**Expected Outcome**: If editing docs/architecture.md with formatting issues, Claude sees errors and fixes them before applying the edit.

---

#### 3. PreToolUse Hook (Pre-Commit for Testing)

**File**: `.claude/hooks/pre_commit.py`

**Purpose**: Runs pytest before git commits to prevent broken commits.

**What it does**:
```python
def pre_commit_hook(context: dict) -> str:
    """Run tests before git commit."""

    # Check if this is a git commit command
    command = context.get('tool_input', {}).get('command', '')

    if 'git commit' in command:
        # Run pytest
        result = subprocess.run(
            ['pytest', 'tests/', '-v', '--tb=short'],
            capture_output=True,
            text=True
        )

        if result.returncode != 0:
            # Tests failed - abort commit
            error_msg = f"""
            ❌ Tests failing - cannot commit

            {result.stdout}
            {result.stderr}

            Fix failing tests before committing.
            """
            return error_msg

    return ""  # Tests passed or not a commit, proceed
```

**Configuration**:
```json
{
  "hooks": {
    "preToolUse": [{
      "matcher": "Bash",
      "hooks": [{
        "type": "python",
        "path": ".claude/hooks/pre_commit.py",
        "symbol": "pre_commit_hook"
      }]
    }]
  }
}
```

**Benefits for Developers**:
- ✅ **TDD discipline enforced** - can't commit broken code
- ✅ Main branch always has passing tests
- ✅ Catches regressions immediately
- ✅ No "I'll fix it later" technical debt

**CLI Usage**: Automatic (runs when Claude executes `git commit`)

**Expected Outcome**:
```
# If tests pass:
[main abc1234] feat: add new feature
3 files changed, 120 insertions(+)

# If tests fail:
❌ Tests failing - cannot commit

tests/test_upload.py::test_upload_pdf FAILED
AssertionError: Expected 200, got 500

Fix failing tests before committing.
```

---

### 💬 Custom Commands in This Project

#### 1. `/start-feature {name}`

**File**: `.claude/commands/start-feature.md`

**Purpose**: Start a new feature by creating symlink and showing task overview.

**What it does**:
1. Validates feature exists in `.work-items/{name}/`
2. Creates symlink: `.claude/plans/{name}-task.plan.md → ../../.work-items/{name}/task.md`
3. Reads user-story.md, design.md, task.md
4. Displays overview: user story, acceptance criteria, first step
5. Commits the symlink creation

**Why chosen**: Automates feature lifecycle start, ensures consistency across all features.

**CLI Usage**:
```bash
/start-feature 03-vector-search-rag
```

**Expected Outcome**:
```
✅ Started feature: 03-vector-search-rag

📖 User Story:
As a Research Analyst, I want to search my knowledge base using natural language queries
so that I can find relevant information across all my documents.

🎯 Acceptance Criteria:
- [ ] Submit query and receive top-K relevant passages
- [ ] See source document and similarity scores
- [ ] Passages with scores above 0.7 for existing content
- [ ] Clear error for empty queries

📋 First Step: 01 - Implement Vector Search Endpoint
Objective: Create POST /search endpoint with vector similarity search

🔴 RED Phase - Write these tests first:
- test_search_returns_relevant_results()
- test_search_with_threshold_filtering()
- test_search_empty_query_returns_400()

Ready to start TDD cycle!
```

**Developer Benefits**:
- Time: 30s vs 5min manual
- Consistency: Same process every time
- Onboarding: Clear starting point for new features

---

#### 2. `/next-step`

**File**: `.claude/commands/next-step.md`

**Purpose**: Identify current step and provide TDD phase guidance.

**What it does**:
1. Finds active feature from `.claude/plans/` symlinks
2. Determines current step number (01, 02, 03, etc.) by checking:
   - Which tests exist
   - Which tests pass/fail
   - Recent git commits
3. Identifies TDD phase (RED/GREEN/REFACTOR)
4. Shows appropriate guidance for current phase

**Why chosen**: Guides TDD workflow, shows exactly what to do next without developer needing to figure it out.

**CLI Usage**:
```bash
/next-step
```

**Expected Outcome (RED phase)**:
```
📍 Active Feature: 02-document-ingestion
📋 Current Step: 03 - Parse and Chunk Documents

🔴 RED Phase: Write Failing Tests

Write these tests in tests/test_parsers.py:

def test_parse_pdf_extracts_text():
    """Test that PDF parser extracts text from all pages."""
    result = parse_pdf("tests/fixtures/sample.pdf")
    assert "expected content" in result
    assert len(result) > 100

def test_chunk_text_creates_passages():
    """Test that chunker creates passages with overlap."""
    text = "word " * 500
    chunks = chunk_text(text, chunk_size=100, overlap=20)
    assert len(chunks) > 1
    assert chunks[0].text[-20:] == chunks[1].text[:20]

Next: Run `pytest tests/test_parsers.py -v` to verify tests fail
```

**Expected Outcome (GREEN phase)**:
```
📍 Active Feature: 02-document-ingestion
📋 Current Step: 03 - Parse and Chunk Documents

🟢 GREEN Phase: Make Tests Pass

Failing tests:
- test_parse_pdf_extracts_text
- test_chunk_text_creates_passages

Implement these components:

1. Create ingestion/parsers.py:
   - parse_pdf(file_path: str) -> str
   - parse_docx(file_path: str) -> str
   - parse_markdown(file_path: str) -> str

2. Create ingestion/chunker.py:
   - chunk_text(text: str, doc_id: str) -> List[Chunk]

Dependencies to add:
- pdfplumber==0.10.3
- python-docx==1.1.0
- langchain-text-splitters==0.2.2

Next: Run `pytest tests/test_parsers.py -v` to verify tests pass
```

**Developer Benefits**:
- No mental overhead: Always know what to do next
- TDD discipline: Guided through RED → GREEN → REFACTOR
- Fast feedback: Immediate next action

---

#### 3. `/verify-step`

**File**: `.claude/commands/verify-step.md`

**Purpose**: Check acceptance criteria and code quality before completing a step.

**What it does**:
1. Identifies current step
2. Runs step-specific tests
3. Extracts acceptance criteria from step file
4. Verifies each criterion with tests
5. Checks code quality (type hints, docstrings, logging, TODOs)
6. Runs full test suite for regressions
7. Generates comprehensive report

**Why chosen**: Enforces verification protocol, prevents premature step completion.

**CLI Usage**:
```bash
/verify-step
```

**Expected Outcome**:
```
🔍 Verification Report: Step 01 - File Upload Endpoint

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

📝 Acceptance Criteria:

✅ Endpoint accepts PDF, DOCX, and Markdown files
   Test: test_upload_pdf, test_upload_docx, test_upload_markdown - PASSED

✅ Invalid file types return 400 error with clear message
   Test: test_upload_unsupported_type - PASSED

✅ Valid uploads return ingestion_id
   Test: test_upload_pdf_returns_ingestion_id - PASSED

✅ Background task queues file for processing
   Test: test_ingestion_pipeline_is_called - PASSED

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

🎯 Test Results:

Step tests: 6/6 passed
Coverage: 92%
Full suite: 46/46 passed

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

✨ Code Quality:

✅ Type hints present
✅ Docstrings complete
✅ Logging implemented
✅ No TODO comments
✅ No print statements
✅ Error handling present

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

📊 Overall Status: ✅ READY TO COMMIT

Suggested commit message:

feat(ingestion): implement file upload endpoint

- Added POST /upload/file endpoint with validation
- Supports PDF, DOCX, and Markdown files
- Returns ingestion_id for tracking
- Queues files for background processing
- Added 6 comprehensive tests (all passing)

Acceptance criteria: All met ✅
Test coverage: 92%

⏱️  Time Tracking:
- Estimated: 2-3 hours
- Actual: 45 minutes
- Time saved: 1.75 hours (70% faster)

🤖 Generated with Claude Code
Co-Authored-By: Claude <noreply@anthropic.com>

Next: Commit this step and move to next with /next-step
```

**Developer Benefits**:
- Confidence: Know exactly what's done/not done
- Quality: Enforced standards before commit
- Time tracking: Automatic calculation
- No forgotten criteria: Systematic verification

---

#### 4. `/complete-feature {name}`

**File**: `.claude/commands/complete-feature.md`

**Purpose**: Verify all acceptance criteria and complete feature lifecycle.

**What it does**:
1. Verifies all numbered steps complete (01, 02, 03, etc.)
2. Checks ALL acceptance criteria from user-story.md
3. Runs full test suite
4. Verifies design compliance
5. Code quality final check
6. Removes symlink from `.claude/plans/`
7. Creates completion commit with time tracking
8. Suggests next feature

**Why chosen**: Comprehensive completion verification, prevents premature feature marking.

**CLI Usage**:
```bash
/complete-feature 02-document-ingestion
```

**Expected Outcome**:
```
🔍 Verifying feature completion: 02-document-ingestion

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

📋 Steps Completed:

✅ Step 01: File Upload Endpoint (6 tests passing)
✅ Step 02: Link Ingestion Endpoint (6 tests passing)
✅ Step 03: Parse and Chunk Documents (9 tests passing)
✅ Step 04: Generate Embeddings (9 tests passing)
✅ Step 05: Persist Artifacts (13 tests passing)

Total: 5/5 steps complete

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

📝 User Story Acceptance Criteria:

✅ Upload PDF, DOCX, or Markdown files
✅ Submit URL for ingestion
✅ Receive error for unsupported types
✅ Documents parsed into chunks
✅ Chunks converted to embeddings
✅ Embeddings stored in Qdrant
✅ Original artifacts saved
✅ Error handling without system failure
✅ Search indexed content

Total: 9/9 criteria met

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

🎯 Test Suite:

Total: 68 tests passed
Coverage: 94%
No regressions detected

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

⏱️  Time Tracking Summary:

Step 01: Estimated 2.5h, Actual 0.75h, Saved 1.75h (70% faster)
Step 02: Estimated 2.5h, Actual 1.0h, Saved 1.5h (60% faster)
Step 03: Estimated 3.0h, Actual 1.0h, Saved 2.0h (67% faster)
Step 04: Estimated 3.0h, Actual 1.25h, Saved 1.75h (58% faster)
Step 05: Estimated 4.0h, Actual 1.5h, Saved 2.5h (63% faster)

Total: Estimated 15h, Actual 5.5h, Saved 9.5h (63% faster)

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

✅ Feature Complete: 02-document-ingestion

Symlink removed, commit created.

🚀 Next Feature Options:

1. 03-vector-search-rag (Retrieval-augmented generation)
2. 04-external-search (External web search integration)
3. 05-answer-synthesis (Critical reasoning and synthesis)

Start next feature with: /start-feature {feature-name}
```

**Developer Benefits**:
- No shortcuts: Can't mark done until ALL criteria met
- Full visibility: See exactly what was accomplished
- Time accountability: Clear productivity metrics
- Smooth transition: Immediate next steps

---

#### 5. `/test-rag [query]`

**File**: `.claude/commands/test-rag.md`

**Purpose**: Quickly test the RAG pipeline end-to-end during development.

**What it does**:
1. Validates Qdrant is running
2. Checks collection exists and has vectors
3. Executes vector search with query
4. Displays results with scores and metadata
5. Assembles RAG context (how it would be sent to LLM)
6. Reports performance metrics (latency, scores, count)

**Why chosen**: Fast pipeline validation without writing test scripts.

**CLI Usage**:
```bash
/test-rag "machine learning basics"
```

**Expected Outcome**:
```
🔍 Testing RAG Pipeline
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Query: "machine learning basics"

✅ Prerequisites:
✅ Qdrant running (http://localhost:6333)
✅ Collection exists (kb_passages)
✅ Vectors indexed: 342 chunks

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

📊 Search Results:

1. Score: 0.847
   Source: ml-introduction.pdf (chunk 3/12)
   Text: Machine learning is a subset of artificial intelligence...

2. Score: 0.823
   Source: ai-fundamentals.docx (chunk 7/15)
   Text: Supervised learning algorithms are trained on labeled data...

3. Score: 0.791
   Source: https://example.com/ml-guide (chunk 2/8)
   Text: The three main types of machine learning are...

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

⏱️  Performance Metrics:

Query latency: 45.2ms
Results returned: 5/5
Average similarity: 0.794
Min score: 0.742
Max score: 0.847

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

✅ RAG Pipeline Test: PASSED

Quality indicators:
✅ Latency < 100ms
✅ Average score > 0.7
✅ All results above threshold
✅ Diverse sources (3 different documents)
✅ Metadata complete

Pipeline ready for production use.
```

**Developer Benefits**:
- Instant feedback: No test file needed
- Quality validation: See if retrieval is good
- Performance visibility: Latency and scores
- Debugging: Quick iteration on queries

---

#### 6. `/ingest {file|url}`

**File**: `.claude/commands/ingest.md`

**Purpose**: Quickly ingest documents or URLs for testing.

**What it does**:
1. Determines if input is file path or URL
2. Validates input (file exists, URL is safe)
3. Runs full ingestion pipeline (parse → chunk → embed → store)
4. Shows progress for each step
5. Reports results (doc_id, chunks created, artifact saved)
6. Optionally verifies storage in Qdrant

**Why chosen**: Easy test data population without API calls.

**CLI Usage**:
```bash
/ingest tests/fixtures/sample.pdf
```

**Expected Outcome**:
```
📄 Ingesting file: tests/fixtures/sample.pdf

[1/4] Parsing document...
      Extracted 12,543 characters from 8 pages

[2/4] Chunking text...
      Created 18 chunks (avg 697 chars/chunk, 200 char overlap)

[3/4] Generating embeddings...
      Generated 18 embeddings (384 dimensions each)
      Embedding time: 0.23s

[4/4] Storing vectors and artifacts...
      Upserted 18 vectors to Qdrant
      Saved artifact to artifacts/uploads/
      Upsert time: 0.15s

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

✅ Ingestion Complete

Doc ID: 3f7b9c42-8d1a-4e5f-9a2c-6b8d1f4e3a7c
Artifact ID: 8a2f5c91-7e3b-4d2a-8c6f-1b9e4a7d3c5f
Chunks created: 18
Status: success
Total time: 0.52s

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

💡 Next steps:

Test retrieval: /test-rag "what is in sample.pdf?"
```

**Developer Benefits**:
- Fast setup: Load test data in seconds
- Integration testing: Full pipeline validation
- Debugging: See each step's output
- Iteration: Quick refine-and-test cycle

---

### 🎓 Skills in This Project

#### 1. genai-specs Skill

**File**: `.claude/skills/genai-specs/skill.md`

**Size**: ~2,900 lines

**Purpose**: Deep understanding of spec-driven development methodology (genai-specs).

**Content Overview**:
- Work item structure (user-story.md, design.md, task.md, step files)
- EARS format (Easy Approach to Requirements Syntax)
- ACID tasks (Atomic, Consistent, Isolated, Durable)
- Verification protocol
- File templates and examples
- Compliance checklist
- Common mistakes to avoid
- Integration with development tools

**When Activated**: When creating/editing user stories, designs, tasks, or organizing work.

**Why Chosen**: Ensures rigorous spec-driven development, prevents incomplete work, maintains single source of truth.

**Example Content**:
```markdown
## EARS Format

Easy Approach to Requirements Syntax:

- **WHEN** {trigger/precondition} **THEN** {system response}
- **IF** {condition} **THEN** {consequent}
- **WHERE** {feature applies} {requirement}
- **WHILE** {state} {requirement}

Example:
- WHEN I upload a PDF file THEN I SHALL receive an ingestion ID within 500ms
- IF I provide an invalid URL THEN I SHALL receive a 400 error with explanation
```

**Developer Benefits**:
- Consistent specifications: Same format every time
- Clear requirements: EARS format removes ambiguity
- AI-friendly: Structured for Claude to understand
- Verification: Clear criteria for completion

---

#### 2. TDD Workflow Skill

**File**: `.claude/skills/tdd-workflow/skill.md`

**Size**: ~2,300 lines

**Purpose**: Test-Driven Development expertise and best practices.

**Content Overview**:
- TDD fundamentals (Red → Green → Refactor)
- Testing best practices (AAA pattern, test naming, fixtures)
- pytest configuration and usage
- Mocking external dependencies
- Project-specific testing patterns
- Common anti-patterns to avoid
- Debugging test failures

**When Activated**: When implementing features, writing tests, refactoring code.

**Why Chosen**: Enforces TDD discipline, provides pytest expertise, prevents testing mistakes.

**Example Content**:
```markdown
## The Three Phases

🔴 **RED Phase**: Write a failing test
- Define expected behavior through tests
- Test should fail for the right reason (not implemented yet)
- Use descriptive test names that explain what is being tested
- One assertion per test when possible

🟢 **GREEN Phase**: Make the test pass with minimal code
- Write simplest code to pass the test
- Don't worry about optimization yet
- Don't add features not covered by tests
- Confirm test passes before moving on

🔵 **REFACTOR Phase**: Improve code quality while keeping tests green
- Extract functions, remove duplication
- Improve names, add documentation
- Optimize performance if needed
- Run tests after each refactoring step
```

**Developer Benefits**:
- TDD mastery: Comprehensive guide to methodology
- pytest expertise: All commands and patterns
- Quality code: Refactoring guidance
- Confidence: Test-first prevents bugs

---

#### 3. RAG Architecture Skill

**File**: `.claude/skills/rag-architecture/skill.md`

**Size**: ~3,500 lines

**Purpose**: Deep technical knowledge of RAG/CAG architecture.

**Content Overview**:
- RAG vs CAG concepts
- Vector embeddings (sentence-transformers, COSINE similarity)
- Document chunking strategy (why 1000 chars, 200 overlap)
- Qdrant configuration and operations
- Ingestion pipeline (parse → chunk → embed → store)
- Firecrawl integration and SSRF protection
- LangChain patterns
- Performance optimization
- Monitoring and debugging
- Common issues and solutions

**When Activated**: When working on RAG/CAG features, vector search, ingestion, retrieval.

**Why Chosen**: Specialized domain knowledge for core system architecture.

**Example Content**:
```markdown
## Chunking Strategy

### Why 1000 characters?

- Balances context vs specificity
- Fits in embedding model's context window
- Enough context for meaningful semantics
- Not so large that irrelevant content dilutes signal

### Why 200 character overlap?

- Prevents splitting related sentences
- Ensures continuity across chunk boundaries
- Helps with cross-chunk queries
- 20% overlap is standard practice

### Algorithm: RecursiveCharacterTextSplitter

Separators priority:
1. Double newline (paragraph breaks) - preferred
2. Single newline (line breaks)
3. Period + space (sentence breaks)
4. Space (word breaks)
5. Character-level (last resort)

This preserves semantic coherence by splitting at natural boundaries.
```

**Developer Benefits**:
- Domain expertise: Deep RAG/CAG knowledge
- Best practices: Why not just what
- Troubleshooting: Common issues and fixes
- Optimization: Performance tuning guide

---

### ⚙️ Configuration Summary

**Bash Permissions** (`.claude/settings.local.json`):
```json
{
  "bash_auto_approve": [
    "tree:*",
    "ls:*",
    "git add:*",
    "git commit:*",
    "git log:*",
    "git status",
    "pytest:*",
    "./venv/bin/pytest:*",
    "./scripts/*.sh:*",
    "curl:*"
  ]
}
```

**Why chosen**: Allow common operations without approval, maintain safety for destructive commands.

**Model**: Claude Sonnet 4.5 (`claude-sonnet-4-5-20250929`)

**Auto-loaded Files** (via pre_prompt hook):
- `.claude/DEVELOPMENT.md` (session context)
- 12 files from `rules/` directory (genai-specs standards)

---

## Part 3: Spec-Driven Development

### What is Spec-Driven Development?

**Definition**: A methodology where specifications (user stories, designs, tasks) are written **before implementation** and serve as the **single source of truth** throughout the development lifecycle.

**Core Philosophy**:
> Specifications define WHAT and WHY (user stories) → Designs define HOW technically (architecture) → Tasks define sequential implementation steps (ACID tasks) → Implementation follows TDD (Red → Green → Refactor) → Verification ensures specifications are met

### The Problems It Solves

| Problem | Traditional Approach | Spec-Driven Solution |
|---------|---------------------|---------------------|
| **Unclear requirements** | "Build a search feature" (vague) | EARS format: "WHEN I submit query THEN I SHALL receive top-5 results ranked by relevance" |
| **Feature creep** | Scope expands during development | Fixed acceptance criteria, out-of-scope section |
| **Lost context** | Why did we build this? | User stories trace every line to user value |
| **Incomplete work** | "It's mostly done..." | Can't mark complete without ALL criteria verified |
| **AI confusion** | Vague instructions → poor results | Structured specs → precise AI implementation |
| **Documentation lag** | Docs written after (if ever) | Specs ARE the documentation |
| **Integration chaos** | Components don't fit together | Design phase ensures coherent architecture |

### The genai-specs Methodology

This project uses **genai-specs**, a specification framework designed for AI-assisted development.

**Repository**: https://github.com/betsalel-williamson/genai-specs

**Key Principles**:
1. **Single Source of Truth**: All specs in `.work-items/`, no duplication
2. **ACID Tasks**: Atomic, Consistent, Isolated, Durable
3. **Verification Protocol**: Never skip verification before marking complete
4. **Small Batch Sizes**: 1-4 hour tasks, frequent commits
5. **Evidence-Based**: No claims without measurement

---

### Implementation in This Project

#### Directory Structure

```
.work-items/
├── 01-project-setup/
│   ├── user-story.md          # WHAT users want
│   ├── design.md              # HOW technically
│   ├── task.md                # Sequential steps
│   ├── 01_init_repo.md        # Step 1 details
│   └── 02_create_env.md       # Step 2 details
├── 02-document-ingestion/
│   ├── user-story.md
│   ├── design.md
│   ├── task.md
│   ├── 01_file_upload_endpoint.md
│   ├── 02_link_ingestion_endpoint.md
│   ├── 03_parse_and_chunk.md
│   ├── 04_generate_embeddings.md
│   └── 05_persist_artifacts.md
├── 03-vector-search-rag/
│   ├── user-story.md
│   ├── design.md
│   ├── task.md
│   ├── 01_vector_search.md
│   ├── 02_retriever_tool.md
│   └── 03_session_memory.md
└── ... (13 features total)
```

#### File Formats

**1. user-story.md** (WHAT users want)

```markdown
# User Story: {Feature Name}

## User Persona

**Name:** Research Analyst
**Description:** Knowledge worker who needs searchable documents

## Story

**As a** Research Analyst
**I want to** upload documents and search them with natural language
**so that** I can find information quickly without manual searching

## Acceptance Criteria (EARS Format)

- WHEN I upload a PDF file THEN I SHALL receive confirmation with ingestion ID
- WHEN I submit a search query THEN I SHALL receive top-5 relevant passages
- IF I upload unsupported file type THEN I SHALL receive clear error message
- WHEN results are returned THEN I SHALL see source citations and scores

## Success Metrics

- ✅ File upload accepts PDF, DOCX, Markdown
- ✅ Search returns results in <100ms
- ✅ Similarity scores >0.7 for relevant content
- ✅ All acceptance criteria met with passing tests
```

**Key Features**:
- **Persona**: Who is this for?
- **User Story**: As/Want/So that format (user-centric)
- **EARS Criteria**: Specific, testable, measurable
- **Success Metrics**: How we verify it works

**2. design.md** (HOW technically)

```markdown
# Design: {Feature Name}

## Objective

{High-level technical goal}

## Technical Design

### Components

**1. Upload Endpoint** (app/routes/upload.py)
- **Purpose**: Accept multipart file uploads
- **Input**: File (PDF/DOCX/Markdown), max 50MB
- **Output**: {"status": "accepted", "ingestion_id": "uuid"}
- **Validation**: MIME type checking, filename sanitization

**2. Ingestion Pipeline** (ingestion/pipeline.py)
- **Purpose**: Orchestrate parse → chunk → embed → store
- **Dependencies**: pdfplumber, python-docx, sentence-transformers
- **Error Handling**: Rollback on failure

### Data Flow

```
User Upload → Validation → Temp Storage → Background Task
                                             ↓
                                     Ingestion Pipeline
                                             ↓
                          Parse → Chunk → Embed → Store in Qdrant
                                             ↓
                                     Save Original Artifact
```

### API Contracts

**POST /upload/file**
Request: multipart/form-data with file field
Response: {"status": "accepted", "ingestion_id": "abc123"}

### Security

- MIME type validation (prevent executable uploads)
- Filename sanitization (prevent directory traversal)
- Max file size: 50MB
- Temp files deleted after processing

### Performance

- Async processing via FastAPI BackgroundTasks
- Batch embedding generation (100 at a time)
- Estimated: 1-2s per 10-page PDF
```

**Key Features**:
- **Components**: What pieces exist
- **Data Flow**: How they connect
- **API Contracts**: Exact request/response formats
- **Security**: Threat model and mitigations
- **Performance**: Expected metrics

**3. task.md** (Sequential implementation)

```markdown
# Task Breakdown: {Feature Name}

## Overview

Complete document ingestion pipeline from upload to vector storage.

## Requirements Traceability

- Links to: user-story.md (Research Analyst needs searchable docs)
- Links to: design.md (Technical architecture)
- Original tasks: Task 03-07 from migration

## Test Strategy

- **Unit Tests**: Parser functions, chunking logic, embedding generation
- **Integration Tests**: End-to-end upload to storage
- **Acceptance Tests**: Verify all EARS criteria from user-story.md

## Sequential Steps (TDD Approach)

### 01 - Implement File Upload Endpoint

**Objective**: Create POST /upload/file endpoint

**Acceptance Criteria**:
- Endpoint accepts PDF, DOCX, Markdown files
- Invalid file types return 400 error
- Valid uploads return ingestion_id
- Background task queues processing

**TDD Cycle**:
1. **Red**: Write tests expecting endpoint to exist and validate file types
2. **Green**: Implement endpoint with validation, temp storage, background tasks
3. **Refactor**: Extract validation logic, add error handling

**Estimated Time**: 2-3 hours

### 02 - Implement Link Ingestion Endpoint

**Objective**: Create POST /upload/link endpoint with Firecrawl

**Acceptance Criteria**:
- Endpoint accepts HTTP/HTTPS URLs
- SSRF validation blocks private IPs
- Firecrawl extracts content
- Content queued for processing

**TDD Cycle**:
1. **Red**: Write URL validation and Firecrawl integration tests
2. **Green**: Implement endpoint with URL safety checks
3. **Refactor**: Extract validation, add retry logic

**Estimated Time**: 2-3 hours

... (more steps)
```

**Key Features**:
- **Traceability**: Links to user-story and design
- **Test Strategy**: How to verify
- **Sequential Steps**: Numbered, estimated, atomic
- **TDD Guidance**: Red → Green → Refactor for each

**4. NN_step.md** (Detailed step implementation)

```markdown
# Step 01: Implement File Upload Endpoint

## Objective

Create REST API endpoint POST /upload/file that accepts multipart file uploads
for PDF, DOCX, and Markdown documents, validates file types, and queues them
for asynchronous ingestion processing.

## Atomic Implementation

This step is atomic: it either creates a working upload endpoint with
validation and background processing, or fails with clear error messages.
No partial state.

## TDD Cycle

### Red Phase

Write failing tests that define expected endpoint behavior:

```python
# tests/test_upload_endpoint.py

def test_upload_pdf_returns_ingestion_id():
    """Test that uploading a valid PDF returns an ingestion ID."""
    file_content = b"%PDF-1.4 fake pdf"
    files = {"file": ("test.pdf", BytesIO(file_content), "application/pdf")}

    response = client.post("/upload/file", files=files)

    assert response.status_code == 200
    assert "ingestion_id" in response.json()

def test_upload_unsupported_type_returns_400():
    """Test that unsupported file types return 400 error."""
    file_content = b"MZ fake exe"
    files = {"file": ("malware.exe", BytesIO(file_content), "application/x-msdownload")}

    response = client.post("/upload/file", files=files)

    assert response.status_code == 400
    assert "Unsupported file type" in response.json()["detail"]
```

**Run tests**: `pytest tests/test_upload_endpoint.py -v`

**Expected**: Tests fail (endpoint doesn't exist yet)

### Green Phase

Implement minimal code to make tests pass:

**1. Create route file**: `app/routes/upload.py`

```python
from fastapi import APIRouter, UploadFile, File, HTTPException
import uuid

router = APIRouter()

SUPPORTED_TYPES = {
    "application/pdf",
    "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
    "text/markdown",
}

@router.post("/file")
async def upload_file(file: UploadFile = File(...)):
    # Validate file type
    if file.content_type not in SUPPORTED_TYPES:
        raise HTTPException(status_code=400, detail=f"Unsupported file type")

    # Generate ingestion ID
    ingestion_id = str(uuid.uuid4())

    # TODO: Queue for processing (next step)

    return {
        "status": "accepted",
        "ingestion_id": ingestion_id,
        "filename": file.filename
    }
```

**2. Register router**: `app/main.py`

```python
from app.routes import upload

app.include_router(upload.router, prefix="/upload", tags=["upload"])
```

**Run tests**: `pytest tests/test_upload_endpoint.py -v`

**Expected**: Tests pass ✅

### Refactor Phase

Improve code quality while keeping tests green:

**Refactoring checklist**:
- [x] Extract validation to helper function
- [x] Add comprehensive docstrings
- [x] Add type hints
- [x] Add logging
- [x] Improve error messages

**Run full test suite**: `pytest tests/ -v`

**Expected**: All tests still pass, code is cleaner

## Completion Criteria

- [ ] All tests passing
- [ ] Type hints present
- [ ] Docstrings complete
- [ ] Logging added
- [ ] No TODO comments
- [ ] Ready to commit
```

**Key Features**:
- **Atomic**: Clear definition of "done"
- **TDD Phases**: Explicit RED → GREEN → REFACTOR
- **Code Examples**: Show exactly what to write
- **Checklists**: Verification steps

---

### Active Work Tracking

**Pattern**: Symlinks in `.claude/plans/` indicate active work.

```
.claude/plans/
├── 02-document-ingestion-task.plan.md → ../../.work-items/02-document-ingestion/task.md
└── (empty when no active work)
```

**Lifecycle**:

1. **Start**: Create symlink
   ```bash
   cd .claude/plans
   ln -s ../../.work-items/02-document-ingestion/task.md 02-document-ingestion-task.plan.md
   git add . && git commit -m "chore: start 02-document-ingestion"
   ```

2. **Work**: Edit through symlink or directly in `.work-items/`
   - Changes sync automatically (symlink)
   - Complete numbered steps sequentially
   - Commit after each step

3. **Complete**: Remove symlink
   ```bash
   rm .claude/plans/02-document-ingestion-task.plan.md
   git add . && git commit -m "feat: complete 02-document-ingestion - all criteria met"
   ```

**Benefits**:
- ✅ Single source of truth (edits sync)
- ✅ Easy discovery (all active work in one dir)
- ✅ Clear lifecycle (presence = active, absence = done)
- ✅ Git-tracked (version control shows status)
- ✅ No duplication (never maintain separate copies)

---

### Workflow Phases

**Phase 1: User Story**
- Define WHAT users want (non-technical)
- Use EARS format for acceptance criteria
- Identify persona and value proposition
- ❌ NO technical details

**Phase 2: Design**
- Define HOW technically
- Components, APIs, data models
- Security, performance, error handling
- Architectural decisions with rationale

**Phase 3: Task Breakdown**
- Granular steps (1-4 hours each)
- Sequential: 01, 02, 03, etc.
- ACID: Atomic, Consistent, Isolated, Durable
- TDD guidance for each step

**Phase 4: Implementation**
- Follow TDD cycle (Red → Green → Refactor)
- Commit after each step
- Separate structural from behavioral changes
- Run tests continuously

**Phase 5: Verification**
- All tests passing
- All acceptance criteria met
- Code quality standards met
- Design implemented as specified

---

### Real Example: 02-document-ingestion

**User Story** (from user-story.md):
```
As a Research Analyst
I want to upload documents and provide web links to be processed and indexed
so that I can search across all my sources to find answers and connections

Acceptance Criteria:
- WHEN I upload a PDF, DOCX, or Markdown file THEN I SHALL receive confirmation
- WHEN I submit a URL THEN I SHALL see the system fetch and process content
- WHEN a document is processed THEN I SHALL see it parsed into searchable chunks
- WHEN chunks are created THEN I SHALL see each converted to vector embedding
- WHEN ingestion completes THEN I SHALL be able to search the indexed content
```

**Design** (from design.md):
```
Components:
1. Upload Endpoint (app/routes/upload.py) - Accept files/URLs
2. Parsers (ingestion/parsers.py) - Extract text from PDF/DOCX/Markdown
3. Chunker (ingestion/chunker.py) - Split text into passages
4. Embeddings (ingestion/embeddings.py) - Generate 384-dim vectors
5. Vector Store (ingestion/vector_store.py) - Qdrant integration
6. Artifacts (ingestion/artifacts.py) - Persist originals
7. Pipeline (ingestion/pipeline.py) - Orchestrate flow

Data Flow:
Upload → Parse → Chunk → Embed → Store Vectors → Save Artifact
```

**Task Breakdown** (from task.md):
```
Step 01: File Upload Endpoint (2-3 hours)
Step 02: Link Ingestion Endpoint (2-3 hours)
Step 03: Parse and Chunk Documents (3-4 hours)
Step 04: Generate Embeddings (3-4 hours)
Step 05: Persist Artifacts & Pipeline (4-5 hours)

Total estimated: 14-19 hours
```

**Actual Implementation**:
- All 5 steps completed
- 68 tests written (all passing)
- 94% code coverage
- Time saved: 9.5 hours (63% faster than estimate)

**Verification**:
- ✅ All 9 EARS acceptance criteria met with tests
- ✅ All design components implemented
- ✅ All 5 steps complete and committed
- ✅ No regressions in test suite
- ✅ Code quality standards met

**Result**: Feature marked complete, symlink removed, completion commit created.

---

### Benefits Demonstrated

**1. Clarity**
- Every feature has clear user value (persona + story)
- Specific acceptance criteria (EARS format)
- No ambiguity about what "done" means

**2. AI Efficiency**
- Structured specs → Claude understands immediately
- Clear tasks → Precise implementation
- TDD guidance → Correct code first time
- Time saved: 63% faster than estimates

**3. Verification**
- Can't mark complete without ALL criteria met
- Systematic testing (unit + integration + acceptance)
- Code quality enforced (type hints, docstrings, logging)

**4. Traceability**
- Every line of code traces to user value
- Git history tracks feature lifecycle
- Acceptance criteria link to tests

**5. Small Batches**
- ACID tasks (1-4 hours) enforce incremental progress
- Frequent commits reduce risk
- Fast feedback loops

---

## Part 4: Cursor vs Claude Code Benchmark

### Feature Comparison Table

| Feature | Cursor IDE | Claude Code | Winner / Notes |
|---------|------------|-------------|----------------|
| **Core Capabilities** |
| Code completion | ✅ Deep inline completion | ❌ Not available | Cursor |
| Chat interface | ✅ GUI panel | ✅ Terminal-based | Tie (different UX) |
| Codebase context | ✅ Project-aware | ✅ 200k token window | Claude Code (larger context) |
| Edit/patch code | ✅ Visual diffs | ✅ Edit tool | Tie (different presentation) |
| Multi-file editing | ✅ Composer mode | ✅ Multi-tool calls | Tie |
| **Extensibility** |
| Hooks | ❌ Not available | ✅ Pre/Post tool hooks | Claude Code exclusive |
| Skills | ❌ Not available | ✅ Markdown-based | Claude Code exclusive |
| Custom commands | ❌ Not available | ✅ Slash commands | Claude Code exclusive |
| MCP integration | ❌ Not available | ✅ Client & server | Claude Code exclusive |
| **Workflow Features** |
| Plans tracking | ✅ Built-in .cursor/plans/ | ⚠️ Manual .claude/plans/ symlinks | Cursor (native integration) |
| Agent modes | ✅ Ask/Manual/Agent | ✅ Task tool subagents | Tie (different approaches) |
| Incremental permissions | ⚠️ Limited | ✅ Granular per-tool | Claude Code |
| Plan-first mode | ❌ Optional | ✅ Default | Claude Code |
| **Developer Experience** |
| Setup time | ✅ ~5 minutes | ⚠️ ~30 minutes | Cursor |
| Learning curve | ✅ Gentle (GUI) | ⚠️ Steeper (CLI) | Cursor |
| Transparency | ⚠️ Some opacity | ✅ Full visibility | Claude Code |
| IDE features | ✅ Full VS Code | ❌ Terminal only | Cursor |
| **Integration** |
| Version control | ✅ VS Code Git UI | ✅ Git CLI | Tie |
| Debugging | ✅ Visual debugger | ⚠️ CLI debugging | Cursor |
| Extensions | ✅ VS Code marketplace | ✅ Claude plugins | Cursor (more mature) |
| Terminal operations | ✅ Integrated terminal | ✅ Native CLI | Tie |

### Claude Code Exclusive Features

#### 1. Hooks System ⭐⭐⭐

**What Cursor has**: Nothing equivalent.

**What Claude Code has**:
- UserPromptSubmit: Auto-inject context every session
- PreToolUse: Validate before any tool execution
- PostToolUse: Verify after tool completes

**Real-world impact**:
```python
# Auto-load 12 genai-specs rules every session
# Without hooks: Manual includes every time (30s overhead)
# With hooks: Automatic (0s overhead, never forgotten)

# Enforce linting before edits
# Without hooks: Remember to run Vale/markdownlint (often skipped)
# With hooks: Automatic (100% compliance, 0 broken docs)

# Enforce testing before commits
# Without hooks: "I'll fix it later" (technical debt)
# With hooks: Can't commit broken code (0 broken commits)
```

**Cursor workaround**: Manual discipline (often fails).

---

#### 2. Skills System ⭐⭐

**What Cursor has**: Nothing equivalent.

**What Claude Code has**:
- Markdown-based specialized knowledge
- On-demand loading (when relevant)
- Reusable across sessions

**Real-world impact**:
```markdown
# Without skills: Explain RAG architecture every session
User: "How does chunking work?"
Claude: "What's the chunk size and overlap?"
User: "1000 chars, 200 overlap" (repeat every session)

# With skills: RAG architecture skill loaded once
User: "How does chunking work?"
Claude: "Based on RAG Architecture skill:
- 1000 char chunks (balance context vs specificity)
- 200 char overlap (prevents splitting sentences)
- RecursiveCharacterTextSplitter (natural boundaries)
Already configured correctly in this project."
```

**Cursor workaround**: Copy-paste from docs (tedious, inconsistent).

---

#### 3. Custom Commands ⭐⭐⭐

**What Cursor has**: Nothing equivalent.

**What Claude Code has**:
- `/start-feature {name}` - Automate feature startup
- `/next-step` - TDD phase guidance
- `/verify-step` - Acceptance criteria verification
- `/complete-feature {name}` - Comprehensive completion
- `/test-rag [query]` - Quick pipeline testing
- `/ingest {file|url}` - Fast data ingestion

**Real-world impact**:
```bash
# Without commands: Manual feature start (5 minutes)
cd .claude/plans
ln -s ../../.work-items/03-vector-search-rag/task.md 03-vector-search-rag-task.plan.md
cat .work-items/03-vector-search-rag/user-story.md
cat .work-items/03-vector-search-rag/design.md
cat .work-items/03-vector-search-rag/task.md
cat .work-items/03-vector-search-rag/01_vector_search.md
# ... read and understand ...

# With commands: Automated feature start (30 seconds)
/start-feature 03-vector-search-rag
# Shows: user story, acceptance criteria, first step, TDD guidance
# Creates symlink automatically
```

**Cursor workaround**: Manual scripts (requires maintenance).

---

#### 4. MCP Integration ⭐

**What Cursor has**: Nothing equivalent.

**What Claude Code has**:
- Connect to any MCP server (databases, APIs, tools)
- Standardized AI-tool interface
- Community ecosystem

**Real-world impact** (potential, not yet used in this project):
```json
// Connect to PostgreSQL
{
  "mcpServers": {
    "postgres": {
      "command": "npx",
      "args": ["-y", "@anthropic-ai/mcp-server-postgres"],
      "env": {"DATABASE_URL": "postgresql://localhost/kb"}
    }
  }
}

// Claude can now:
User: "Show me the most ingested documents this month"
Claude: [queries database via MCP]
       "Top 5 documents:
       1. ml-introduction.pdf (45 times)
       2. python-guide.md (38 times)
       ..."
```

**Cursor workaround**: Write custom scripts (not standardized).

---

### Cursor Exclusive Features

#### 1. Inline Code Completion ⭐⭐⭐

**What Claude Code has**: Nothing (terminal-based, no inline).

**What Cursor has**:
- Deep autocomplete as you type
- Context-aware suggestions
- Multi-line predictions
- Tab to accept

**Real-world impact**:
```python
# Cursor: Type "def parse" → suggests entire function
def parse_pdf(file_path: str) -> str:
    """Extract text from PDF."""
    with pdfplumber.open(file_path) as pdf:
        return "\n".join(page.extract_text() for page in pdf.pages)
# (Just press Tab to accept)

# Claude Code: Must describe or copy-paste
User: "Create parse_pdf function that extracts text using pdfplumber"
Claude: [writes code in response]
User: [copies to file]
```

**Claude Code workaround**: None (fundamental difference).

---

#### 2. Visual Interface ⭐⭐

**What Claude Code has**: Terminal only.

**What Cursor has**:
- GUI chat panel
- Visual diffs with colors
- Clickable file navigation
- Syntax highlighting in editor

**Real-world impact**:
```
# Cursor: See diff visually
- old line (red background)
+ new line (green background)

# Claude Code: See diff as text
--- a/file.py
+++ b/file.py
@@ -10,3 +10,3 @@
-old line
+new line
```

**Claude Code workaround**: Use external diff tools (git diff, diffuse).

---

#### 3. VS Code Ecosystem ⭐⭐

**What Claude Code has**: None (not based on VS Code).

**What Cursor has**:
- Full VS Code feature set
- Extensions marketplace
- Integrated debugging
- GUI settings

**Real-world impact**:
- Cursor: Install Python extension, get debugger, linting, IntelliSense
- Claude Code: Use terminal debugger (pdb), CLI linters

**Claude Code workaround**: Use separate editor + Claude Code in terminal.

---

#### 4. Built-in Plans Integration ⭐

**What Claude Code has**: Manual symlinks in `.claude/plans/`.

**What Cursor has**:
- Native `.cursor/plans/` feature
- GUI integration
- Automatic tracking

**Real-world impact**:
```
# Cursor: Built-in plans UI
- Shows active plans in sidebar
- Click to open
- Automatic status tracking

# Claude Code: Manual symlink management
- ls .claude/plans/ (see active work)
- Use scripts (./scripts/start-feature.sh)
- Or use /start-feature command
```

**Claude Code workaround**: Custom commands + scripts (works well, but not native).

---

### When to Use What?

#### Use Claude Code When:

✅ **Terminal-heavy workflow**
- Backend development (Python, Go, Rust)
- DevOps/infrastructure work
- CLI tool development

✅ **Need hooks/skills/commands**
- Enforcing standards automatically
- Injecting specialized knowledge
- Workflow automation

✅ **Large codebase**
- 200k token context advantage
- Full project visibility

✅ **Value transparency**
- Want to see every action
- Need fine-grained control
- Learning AI capabilities

✅ **Complex planning**
- Plans-first approach
- Architectural decisions
- System design

✅ **Need MCP integration**
- Connect to databases
- External API integration
- Custom tool protocols

---

#### Use Cursor When:

✅ **Need inline completion**
- Rapid prototyping
- Writing boilerplate
- Exploratory coding

✅ **Visual editing preferred**
- Frontend development (React, Vue)
- Visual design work
- Prefer GUI over CLI

✅ **Less technical team**
- Designers, product managers
- Lower learning curve
- Familiar VS Code environment

✅ **Quick setup critical**
- New project (fast start)
- Trying out AI coding
- Time-constrained

✅ **Want IDE features**
- Visual debugging
- GUI settings
- Extension ecosystem

---

### This Project's Choice: Claude Code

**Why Claude Code for knowledge-agent?**

1. **RAG/CAG requires thoughtful planning**
   - Plans-first approach essential
   - Complex architecture (vector search, embeddings, LLM chains)
   - Need to think before coding

2. **TDD discipline enforced**
   - Pre-commit hook prevents broken commits
   - Can't skip tests with hooks
   - Rigorous quality standards

3. **Terminal workflow fits stack**
   - Python/FastAPI backend
   - pytest testing
   - Docker/Qdrant
   - Git CLI

4. **Hooks ensure quality**
   - Auto-load genai-specs rules (consistency)
   - Documentation linting (no broken docs)
   - Test enforcement (no broken code)

5. **Skills provide expertise**
   - genai-specs methodology (spec-driven)
   - TDD workflow (testing discipline)
   - RAG architecture (domain knowledge)

6. **Commands automate workflow**
   - /start-feature (consistent feature start)
   - /next-step (TDD guidance)
   - /verify-step (acceptance verification)
   - /complete-feature (comprehensive completion)

7. **Full codebase context**
   - 200k tokens fits entire project
   - Can reason about architecture
   - Cross-file refactoring

**Result**: 63% faster development than estimates, 94% test coverage, 0 broken commits.

---

### Feature Mapping

| Cursor Feature | Claude Code Equivalent | Notes |
|----------------|------------------------|-------|
| .cursor/plans/ | .claude/plans/ (manual symlinks) | Same pattern, manual implementation |
| Inline completion | ❌ None | Fundamental difference (terminal vs IDE) |
| Composer mode | Multiple tool calls | Same capability, different UX |
| Chat panel | Terminal chat | Same AI, different interface |
| Agent modes | Task tool subagents | Similar concept, different implementation |
| VS Code features | ❌ Terminal only | Use separate editor if needed |
| ❌ No hooks | Hooks system | Claude Code exclusive |
| ❌ No skills | Skills system | Claude Code exclusive |
| ❌ No commands | Slash commands | Claude Code exclusive |
| ❌ No MCP | MCP client/server | Claude Code exclusive |

---

### Hybrid Approach (Best of Both?)

**Possible hybrid workflow**:

1. **Use Cursor for**:
   - Fast prototyping (inline completion)
   - Exploring unfamiliar code
   - Visual editing (CSS, React)

2. **Use Claude Code for**:
   - Feature planning (.claude/plans/)
   - Quality enforcement (hooks)
   - TDD workflow (commands)
   - Final implementation (rigorous)

3. **Share**:
   - Same .work-items/ specs
   - Same git repository
   - Same test suite

**Trade-offs**:
- Context switching overhead
- Need to learn both tools
- Potential consistency issues

**Recommendation**: Pick one based on team strengths and stick with it. This project demonstrates Claude Code can achieve excellent results alone.

---

## Conclusion & Recommendations

### Key Takeaways

1. **AI coding is about more than autocomplete**
   - Hooks enforce standards
   - Skills inject knowledge
   - Commands automate workflows
   - Specs drive implementation

2. **Rigorous methodology scales with AI**
   - genai-specs provides structure
   - TDD enforced via hooks
   - Small batches reduce risk
   - Verification prevents incomplete work

3. **Claude Code excels at systematic development**
   - Plans-first approach
   - Extensible plugin system
   - Transparent execution
   - Fine-grained control

4. **Cursor excels at rapid prototyping**
   - Inline completion speeds typing
   - Visual interface lowers barrier
   - Fast setup gets started quickly
   - IDE features familiar to devs

### Recommendations for ML Teams

**For Backend/Infrastructure Teams**:
- ✅ Use Claude Code
- Leverage hooks for quality
- Create project-specific skills
- Automate workflows with commands

**For Full-Stack Teams**:
- ⚠️ Evaluate both
- Claude Code for backend/APIs
- Cursor for frontend/UI
- Or pick one for consistency

**For Research/Prototyping Teams**:
- ✅ Use Cursor
- Fast iteration critical
- Inline completion helps exploration
- Visual interface preferred

**For Production Systems**:
- ✅ Use Claude Code
- Rigor and quality critical
- Hooks prevent mistakes
- Spec-driven ensures completeness

### Implementation Checklist

**If choosing Claude Code**:

1. **Setup** (Week 1)
   - [ ] Install Claude Code CLI
   - [ ] Create .claude/ directory structure
   - [ ] Configure basic settings.json
   - [ ] Set up pre-prompt hook (auto-load context)

2. **Core Features** (Week 2-3)
   - [ ] Create project-specific skills (2-3)
   - [ ] Write workflow commands (4-6)
   - [ ] Configure bash permissions
   - [ ] Set up pre-commit hook (testing)

3. **Spec-Driven** (Week 4)
   - [ ] Create .work-items/ structure
   - [ ] Write first feature spec (user-story + design + task)
   - [ ] Implement with TDD
   - [ ] Use commands for workflow

4. **Optimization** (Ongoing)
   - [ ] Refine hooks based on usage
   - [ ] Expand skills with new knowledge
   - [ ] Create more commands for common tasks
   - [ ] Consider MCP integration for external tools

**If choosing Cursor**:

1. **Setup** (Day 1)
   - [ ] Install Cursor IDE
   - [ ] Sign up for account
   - [ ] Open project in Cursor

2. **Workflow** (Week 1)
   - [ ] Learn inline completion (Tab)
   - [ ] Use Composer for multi-file edits
   - [ ] Try different agent modes
   - [ ] Explore .cursor/plans/ (optional)

3. **Quality** (Week 2)
   - [ ] Set up pre-commit hooks (git hooks, not Cursor hooks)
   - [ ] Configure linters/formatters
   - [ ] Establish testing discipline (manual)

4. **Scaling** (Ongoing)
   - [ ] Create .cursor/plans/ for complex features
   - [ ] Write custom VS Code tasks
   - [ ] Build team coding standards doc

---

### Final Thoughts

This project demonstrates that **rigorous software engineering and AI assistance are not contradictory**. In fact, they're synergistic:

- **Specs guide AI** → Better implementations
- **Hooks enforce quality** → Fewer mistakes
- **Skills inject knowledge** → Domain expertise
- **Commands automate workflow** → Faster execution
- **TDD + AI** → Correct code first time

**The result**: 63% faster development, 94% test coverage, 0 broken commits, clear traceability from user value to implementation.

**The key**: Don't just use AI as a smarter autocomplete. Use it as a **force multiplier** for systematic, high-quality software engineering.

---

## References

**Claude Code**:
- Official Docs: https://docs.claude.com/en/docs/claude-code
- GitHub: https://github.com/anthropics/claude-code

**genai-specs**:
- Repository: https://github.com/betsalel-williamson/genai-specs
- EARS Format: https://alistairmavin.com/ears/

**Project Files**:
- Configuration: `.claude/settings.json`, `.claude/settings.local.json`
- Hooks: `.claude/hooks/pre_prompt.py`, `pre_patch.py`, `pre_commit.py`
- Commands: `.claude/commands/*.md` (6 commands)
- Skills: `.claude/skills/**/*.md` (3 skills)
- Rules: `rules/*.mdc` (12 files)
- Work Items: `.work-items/` (13 features)
- Plans: `.claude/plans/README.md`

**Methodology**:
- Test-Driven Development: Kent Beck, "Test-Driven Development: By Example"
- Tidy First?: Kent Beck, "Tidy First?"
- Small Batch Sizes: DevOps Research & Assessment (DORA)

---

**Document Status**: Complete
**Version**: 1.0
**Last Updated**: November 6, 2025
**Maintained By**: Project Team
**Review Cycle**: Quarterly or when major Claude Code updates

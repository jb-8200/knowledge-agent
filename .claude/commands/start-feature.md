Start a new feature by creating a symlink in .claude/plans/ and displaying the task overview.

## Usage

```
/start-feature 03-vector-search-rag
```

## What This Does

1. **Creates symlink**: `.claude/plans/{feature-name}-task.plan.md → ../../.work-items/{feature-name}/task.md`
2. **Reads work item files**: `user-story.md`, `design.md`, `task.md`
3. **Displays overview**: Shows user story, acceptance criteria, and first step
4. **Ready to code**: Guides you to start with step 01

## Steps

### 1. Validate Feature Exists

Check that `.work-items/{feature-name}/` directory exists:

```bash
test -d .work-items/{{feature-name}} && echo "Feature found" || echo "ERROR: Feature not found"
```

### 2. Create Symlink

```bash
cd .claude/plans
ln -s ../../.work-items/{{feature-name}}/task.md {{feature-name}}-task.plan.md
cd ../..
```

### 3. Read Work Item Context

Display the following files to understand the feature:

- `.work-items/{{feature-name}}/user-story.md` - What we're building and why
- `.work-items/{{feature-name}}/design.md` - Technical architecture
- `.work-items/{{feature-name}}/task.md` - Step-by-step breakdown

### 4. Show First Step

Read `.work-items/{{feature-name}}/01_*.md` and display:
- Objective
- Acceptance criteria
- TDD Red phase (what tests to write)

### 5. Commit the Start

```bash
git add .claude/plans/
git commit -m "chore: start {{feature-name}}

Created symlink to mark feature as active.

🤖 Generated with Claude Code
Co-Authored-By: Claude <noreply@anthropic.com>"
```

## Output Format

After running this command, you should see:

```
✅ Started feature: {feature-name}

📖 User Story:
As a {persona}, I want {capability} so that {benefit}

🎯 Acceptance Criteria:
- [ ] Criterion 1
- [ ] Criterion 2
- [ ] Criterion 3

📋 First Step: 01 - {step title}
Objective: {objective}

🔴 RED Phase - Write these tests first:
{test descriptions}

Ready to start TDD cycle! Use /next-step to see detailed guidance.
```

## Example

```
/start-feature 03-vector-search-rag
```

Output:
```
✅ Started feature: 03-vector-search-rag

📖 User Story:
As a Research Analyst, I want to search my knowledge base using natural language queries so that I can find relevant information across all my documents.

🎯 Acceptance Criteria:
- [ ] Search endpoint accepts text queries
- [ ] Returns top 5 relevant chunks with similarity scores
- [ ] Includes source metadata and citations

📋 First Step: 01 - Implement Vector Search Endpoint
Objective: Create POST /search endpoint with vector similarity search

🔴 RED Phase - Write these tests first:
- test_search_returns_relevant_results()
- test_search_with_threshold_filtering()
- test_search_empty_query_returns_400()

Ready to start TDD cycle! Use /next-step for detailed guidance.
```

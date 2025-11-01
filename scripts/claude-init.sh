#!/usr/bin/env bash
#
# claude-init.sh – Bootstrap a new Claude Code session.
#
# This script verifies that the rules directory exists with all necessary
# specification files, creates a minimal .env if necessary, and prints a
# kickoff prompt that instructs Claude Code to use the project rules.
#
# Note: This project uses a COPY (not submodule) approach for genai-specs.
# Files are copied once from https://github.com/betsalel-williamson/genai-specs
# and are not automatically synced.

set -e

PROJECT_ROOT="$(dirname "$0")/.."
RULES_DIR="$PROJECT_ROOT/rules"

# Check if rules directory exists and has the core files
if [ ! -d "$RULES_DIR" ]; then
  echo "🚫 Rules directory not found. Please run the setup script to copy genai-specs files."
  exit 1
fi

# Verify core process files exist
CORE_FILES=(
  "process-01-core.mdc"
  "process-02-project.mdc"
  "process-03-development.mdc"
  "process-04-operational.mdc"
  "process-05-coding.mdc"
)

for file in "${CORE_FILES[@]}"; do
  if [ ! -f "$RULES_DIR/$file" ]; then
    echo "🚫 Missing required file: rules/$file"
    echo "Please run scripts/copy-genai-specs.sh to download specification files."
    exit 1
  fi
done

# Check .env file
ENV_FILE="$PROJECT_ROOT/.env"
if [ ! -f "$ENV_FILE" ]; then
  cat <<ENV >"$ENV_FILE"
# Minimal environment for local development
LLM_PROVIDER=local
EMBEDDING_MODEL=sentence-transformers/all-MiniLM-L6-v2
QDRANT_URL=http://localhost:6333
FIRECRAWL_API_KEY=your_api_key_here
ENV
  echo "✅ Created .env file with default values"
fi

# Print kickoff prompt
cat <<PROMPT

📋 Project rules are configured via .claude/settings.json

The following files are always included:
  • Core Process (rules/process-01-core.mdc through process-05-coding.mdc)
  • Standards (rules/standards-*.mdc)

Technology-specific guidelines are auto-loaded by file extension:
  • .py → guidelines-python.mdc
  • .ts/.tsx → guidelines-typescript.mdc
  • .js/.jsx → guidelines-javascript.mdc

You may explicitly reference any rule file with @./rules/<file>.mdc

⏱️  Time Tracking Enabled:
  • Each step has time estimates in task.md files
  • Track actual time: start-feature.sh → complete-feature.sh
  • Add time saved to commit messages (see .claude/plans/README.md)
  • Format: Estimated vs Actual vs Time Saved

Ready to proceed with spec-driven development!
PROMPT

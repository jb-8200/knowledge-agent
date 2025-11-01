#!/usr/bin/env bash
#
# copy-genai-specs.sh – Download specification files from genai-specs repo.
#
# This script fetches the core process, standards, and technology-specific
# guideline files from the genai-specs repository and copies them to the
# rules/ directory. Run this script to update your local copies.

set -e

PROJECT_ROOT="$(dirname "$0")/.."
RULES_DIR="$PROJECT_ROOT/rules"
BASE_URL="https://raw.githubusercontent.com/betsalel-williamson/genai-specs/main/rules"

# Ensure rules directory exists
mkdir -p "$RULES_DIR"

echo "📥 Downloading genai-specs files..."

# Core Process Files (Always Included)
CORE_FILES=(
  process-01-core.mdc
  process-02-project.mdc
  process-03-development.mdc
  process-04-operational.mdc
  process-05-coding.mdc
)

echo "  → Core process files..."
for file in "${CORE_FILES[@]}"; do
  curl -fsSL "$BASE_URL/$file" -o "$RULES_DIR/$file"
  echo "    ✓ $file"
done

# Standards Files (Always Included)
STANDARDS_FILES=(
  standards-user-story.mdc
  standards-design.mdc
  standards-task.mdc
  standards-architecture.mdc
  standards-decision.mdc
  standards-guidelines.mdc
)

echo "  → Standards files..."
for file in "${STANDARDS_FILES[@]}"; do
  curl -fsSL "$BASE_URL/$file" -o "$RULES_DIR/$file"
  echo "    ✓ $file"
done

# Technology Guidelines (Conditional Inclusion)
GUIDELINE_FILES=(
  guidelines-python.mdc
  guidelines-typescript.mdc
  guidelines-javascript.mdc
  guidelines-testing.mdc
  guidelines-verification-protocol.mdc
  guidelines-docker.mdc
  guidelines-github.mdc
)

echo "  → Technology guidelines..."
for file in "${GUIDELINE_FILES[@]}"; do
  curl -fsSL "$BASE_URL/$file" -o "$RULES_DIR/$file"
  echo "    ✓ $file"
done

# Linting Configuration Files
echo "  → Linting configuration..."
curl -fsSL "https://raw.githubusercontent.com/betsalel-williamson/genai-specs/main/.vale.ini" \
  -o "$PROJECT_ROOT/.vale.ini"
echo "    ✓ .vale.ini"

curl -fsSL "https://raw.githubusercontent.com/betsalel-williamson/genai-specs/main/.markdownlint-cli2.yaml" \
  -o "$PROJECT_ROOT/.markdownlint-cli2.yaml"
echo "    ✓ .markdownlint-cli2.yaml"

echo ""
echo "✅ All genai-specs files downloaded successfully!"
echo ""
echo "Files are stored in:"
echo "  • $RULES_DIR/"
echo "  • $PROJECT_ROOT/.vale.ini"
echo "  • $PROJECT_ROOT/.markdownlint-cli2.yaml"

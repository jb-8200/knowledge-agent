#!/usr/bin/env bash
#
# complete-feature.sh - Mark feature work as complete (genai-specs pattern)
#
# Usage: ./scripts/complete-feature.sh <feature-name>
# Example: ./scripts/complete-feature.sh 01-project-setup
#
# This script removes the symbolic link from .claude/plans/, indicating that
# work on this feature is complete. Before removing, it verifies that all
# acceptance criteria have been met (genai-specs requirement).
# This pattern is adapted from genai-specs Cursor Plans for Claude Code.

set -euo pipefail

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

# Project root (script is in scripts/ subdirectory)
PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

# Directories
WORK_ITEMS_DIR="${PROJECT_ROOT}/.work-items"
PLANS_DIR="${PROJECT_ROOT}/.claude/plans"

# Function to print usage
usage() {
    echo "Usage: $0 <feature-name>"
    echo
    echo "Examples:"
    echo "  $0 01-project-setup"
    echo "  $0 02-document-ingestion"
    echo "  $0 05-answer-synthesis"
    echo
    echo "Currently active features:"
    if [ -d "${PLANS_DIR}" ] && [ "$(ls -A "${PLANS_DIR}"/*.plan.md 2>/dev/null)" ]; then
        for plan in "${PLANS_DIR}"/*.plan.md; do
            basename "$plan" | sed 's/-task\.plan\.md$//'
        done
    else
        echo "  (no active work)"
    fi
    exit 1
}

# Check arguments
if [ $# -ne 1 ]; then
    echo -e "${RED}Error: Feature name required${NC}" >&2
    usage
fi

FEATURE_NAME="$1"

# Validate feature exists
FEATURE_DIR="${WORK_ITEMS_DIR}/${FEATURE_NAME}"
USER_STORY_FILE="${FEATURE_DIR}/user-story.md"
TASK_FILE="${FEATURE_DIR}/task.md"

if [ ! -d "${FEATURE_DIR}" ]; then
    echo -e "${RED}Error: Feature directory not found: ${FEATURE_DIR}${NC}" >&2
    exit 1
fi

# Symlink name following genai-specs convention
SYMLINK_NAME="${FEATURE_NAME}-task.plan.md"
SYMLINK_PATH="${PLANS_DIR}/${SYMLINK_NAME}"

# Check if symlink exists (feature is active)
if [ ! -e "${SYMLINK_PATH}" ]; then
    echo -e "${RED}Error: Feature is not marked as active work${NC}" >&2
    echo
    echo "Symlink not found: ${SYMLINK_PATH}"
    echo
    echo "Currently active features:"
    if [ -d "${PLANS_DIR}" ] && [ "$(ls -A "${PLANS_DIR}"/*.plan.md 2>/dev/null)" ]; then
        ls -1 "${PLANS_DIR}"/*.plan.md | xargs -n1 basename | sed 's/-task\.plan\.md$//'
    else
        echo "  (no active work)"
    fi
    echo
    echo "Did you forget to run: ./scripts/start-feature.sh ${FEATURE_NAME}"
    exit 1
fi

# Display verification checklist
echo -e "${CYAN}=== Feature Completion Verification ===${NC}"
echo
echo "Feature: ${FEATURE_NAME}"
echo "Location: ${FEATURE_DIR}"
echo
echo -e "${YELLOW}Before marking complete, verify ALL of the following:${NC}"
echo

# Check if user-story.md exists and display acceptance criteria
if [ -f "${USER_STORY_FILE}" ]; then
    echo "📋 Acceptance Criteria (from user-story.md):"
    echo
    # Extract EARS format criteria (lines with WHEN/IF/WHILE... THEN... SHALL...)
    if grep -q "WHEN\|IF\|WHILE" "${USER_STORY_FILE}"; then
        grep -E "^\s*-\s*(WHEN|IF|WHILE)" "${USER_STORY_FILE}" || true
    else
        echo "  (see ${USER_STORY_FILE} for criteria)"
    fi
    echo
else
    echo -e "${YELLOW}⚠️  user-story.md not found - cannot verify acceptance criteria${NC}"
    echo
fi

# Display verification checklist from genai-specs
echo "✅ Verification Checklist (genai-specs requirements):"
echo "  [ ] ALL acceptance criteria met"
echo "  [ ] ALL tests passing"
echo "  [ ] ALL numbered steps complete (01, 02, 03, etc.)"
echo "  [ ] Design fully implemented"
echo "  [ ] ALL changes committed to git"
echo
echo -e "${RED}⚠️  From genai-specs:${NC}"
echo '  "Prematurely marking tasks as complete can lead to'
echo '   incomplete work and hinder project progress."'
echo

# Prompt for confirmation
read -p "Have you verified ALL items above? (y/N): " -n 1 -r
echo

if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    echo -e "${YELLOW}Aborted. Feature still marked as active work.${NC}"
    echo
    echo "When ready to complete, run this script again:"
    echo "  ./scripts/complete-feature.sh ${FEATURE_NAME}"
    exit 0
fi

# Double confirmation for safety
echo
read -p "Are you ABSOLUTELY SURE all criteria are met? (yes/NO): " -r
echo

if [[ ! $REPLY =~ ^(yes|YES)$ ]]; then
    echo -e "${YELLOW}Aborted. Feature still marked as active work.${NC}"
    exit 0
fi

# Remove the symlink
rm "${SYMLINK_PATH}"

# Verify symlink removed
if [ ! -e "${SYMLINK_PATH}" ]; then
    echo -e "${GREEN}✅ Completed: ${FEATURE_NAME}${NC}"
    echo
    echo "Removed symlink: ${SYMLINK_PATH}"
    echo
    echo "Next steps:"
    echo "  1. Commit the change:"
    echo "     git add .claude/plans/"
    echo "     git commit -m \"Complete ${FEATURE_NAME} - all criteria met\""
    echo
    echo "  2. Original task documentation preserved at:"
    echo "     ${FEATURE_DIR}"
    echo
    echo "  3. Check remaining active work:"
    echo "     ls .claude/plans/"
    echo
    echo "  4. Start next feature:"
    echo "     ./scripts/start-feature.sh <next-feature-name>"
else
    echo -e "${RED}Error: Failed to remove symlink${NC}" >&2
    exit 1
fi

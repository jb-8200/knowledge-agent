#!/usr/bin/env bash
#
# start-feature.sh - Start active work on a feature (genai-specs pattern)
#
# Usage: ./scripts/start-feature.sh <feature-name>
# Example: ./scripts/start-feature.sh 01-project-setup
#
# This script creates a symbolic link in .claude/plans/ pointing to the
# feature's task.md file, indicating that work on this feature is active.
# This pattern is adapted from genai-specs Cursor Plans for Claude Code.

set -euo pipefail

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
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
    echo "Available features:"
    if [ -d "${WORK_ITEMS_DIR}" ]; then
        ls -1 "${WORK_ITEMS_DIR}" | grep -E "^[0-9]" || echo "  (none found)"
    else
        echo "  (${WORK_ITEMS_DIR} not found)"
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
TASK_FILE="${FEATURE_DIR}/task.md"

if [ ! -d "${FEATURE_DIR}" ]; then
    echo -e "${RED}Error: Feature directory not found: ${FEATURE_DIR}${NC}" >&2
    echo
    echo "Available features:"
    ls -1 "${WORK_ITEMS_DIR}" | grep -E "^[0-9]" || echo "  (none found)"
    exit 1
fi

if [ ! -f "${TASK_FILE}" ]; then
    echo -e "${RED}Error: task.md not found in feature directory: ${TASK_FILE}${NC}" >&2
    exit 1
fi

# Create .claude/plans/ directory if it doesn't exist
if [ ! -d "${PLANS_DIR}" ]; then
    echo -e "${YELLOW}Creating .claude/plans/ directory...${NC}"
    mkdir -p "${PLANS_DIR}"
fi

# Symlink name following genai-specs convention
SYMLINK_NAME="${FEATURE_NAME}-task.plan.md"
SYMLINK_PATH="${PLANS_DIR}/${SYMLINK_NAME}"

# Check if symlink already exists
if [ -e "${SYMLINK_PATH}" ]; then
    echo -e "${YELLOW}Warning: Symlink already exists for ${FEATURE_NAME}${NC}"
    echo "This feature is already marked as active work."
    echo
    echo "Symlink: ${SYMLINK_PATH}"
    ls -l "${SYMLINK_PATH}"
    echo
    read -p "Recreate symlink? (y/N): " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        echo "Aborted."
        exit 0
    fi
    rm "${SYMLINK_PATH}"
fi

# Create relative symlink
# From .claude/plans/ to .work-items/{feature}/task.md
RELATIVE_TARGET="../../.work-items/${FEATURE_NAME}/task.md"

cd "${PLANS_DIR}"
ln -s "${RELATIVE_TARGET}" "${SYMLINK_NAME}"
cd "${PROJECT_ROOT}"

# Verify symlink created successfully
if [ -L "${SYMLINK_PATH}" ]; then
    echo -e "${GREEN}✅ Started work on: ${FEATURE_NAME}${NC}"
    echo
    echo "Created symlink:"
    ls -l "${SYMLINK_PATH}"
    echo
    echo "Next steps:"
    echo "  1. Commit the change:"
    echo "     git add .claude/plans/"
    echo "     git commit -m \"Start ${FEATURE_NAME}\""
    echo
    echo "  2. Read the feature documentation:"
    echo "     - ${FEATURE_DIR}/user-story.md"
    echo "     - ${FEATURE_DIR}/design.md"
    echo "     - ${FEATURE_DIR}/task.md"
    echo
    echo "  3. Begin TDD cycle on first numbered step"
    echo
    echo "  4. When complete, run:"
    echo "     ./scripts/complete-feature.sh ${FEATURE_NAME}"
    echo
    echo "See .claude/plans/README.md for full documentation."
else
    echo -e "${RED}Error: Failed to create symlink${NC}" >&2
    exit 1
fi

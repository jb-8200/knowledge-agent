# Spec 33 – Write a bootstrap script for Claude Code

This specification describes how to implement a shell script
(`scripts/claude-init.sh`) that bootstraps a Claude Code session.  The
script ensures the development environment is configured correctly and
provides a kickoff prompt to instruct Claude on which rules to load.

## Steps

1. **Verify the `genai-specs` submodule.**  The script should check
   whether a directory named `genai-specs` exists in the project root.
   If it does not, print an error message instructing the developer to
   add the submodule:

   ```sh
   git submodule add https://github.com/betsalel-williamson/genai-specs
   ```

   The script must exit with a non‑zero status if the submodule is missing.

2. **Ensure the rules directory exists.**  Check if the `rules/`
   directory is present.  If not, create it.  Do not remove or
   overwrite existing files in this directory.

3. **Create a minimal `.env` file.**  If no `.env` file exists in the
   project root, generate one with placeholder values for the LLM
   provider, embedding model, Qdrant URL, Firecrawl API key and other
   configuration keys.  Leave the file untouched if it already exists.

4. **Print the kickoff prompt.**  The script should output a prompt
   instructing the developer (or Claude Code) to include the core
   specification files at the beginning of a session.  The prompt
   should list each file using the `@./rules/filename` syntax.  For
   example:

   ```
   Please load the following project rules before starting:
     @./rules/process-01.mdc
     @./rules/process-02.mdc
     ...
     @./rules/standards-decision.mdc
   
   Then you may proceed with the current work item.
   ```

5. **Mark the script as executable.**  After creating the file,
   ensure it has execute permissions (`chmod +x scripts/claude-init.sh`).

## Code Example

The following snippet illustrates the structure of the script:

```bash
#!/usr/bin/env bash
set -e

PROJECT_ROOT="$(dirname "$0")/.."

if [ ! -d "$PROJECT_ROOT/genai-specs" ]; then
  echo "🚫 genai-specs submodule not found. Please run:"
  echo "    git submodule add https://github.com/betsalel-williamson/genai-specs"
  exit 1
fi

mkdir -p "$PROJECT_ROOT/rules"

ENV_FILE="$PROJECT_ROOT/.env"
if [ ! -f "$ENV_FILE" ]; then
  cat <<ENV >"$ENV_FILE"
# Default environment for local development
LLM_PROVIDER=local
EMBEDDING_MODEL=sentence-transformers/all-MiniLM-L6-v2
QDRANT_URL=http://localhost:6333
FIRECRAWL_API_KEY=your_api_key_here
ENV
fi

cat <<PROMPT
Please load the following project rules before starting:
  @./rules/process-01.mdc
  @./rules/process-02.mdc
  @./rules/process-03.mdc
  @./rules/process-04.mdc
  @./rules/process-05.mdc
  @./rules/standards-design.mdc
  @./rules/standards-task.mdc
  @./rules/standards-architecture.mdc
  @./rules/standards-decision.mdc

Then you may proceed with the current work item.
PROMPT
```

This example checks for the submodule, creates a rules directory and a
default `.env` file and prints the kickoff prompt.  Adjust the
environment variables according to your infrastructure.
    Summary

     Add 7 custom slash commands and 3 custom skills to enhance the knowledge-agent development workflow, all aligned with 
     genai-specs standards and TDD practices.

     Proposed Implementation

     Phase 1: Directory Structure (1 minute)

     mkdir -p .claude/commands
     mkdir -p .claude/skills/{rag-architecture,tdd-workflow,genai-specs-docs}

     Phase 2: Priority Slash Commands (10 minutes)

     P0 Commands (implement first):
     1. /tdd-task <feature> <task-num> - Guide TDD implementation with Red→Green→Refactor cycle
     2. /verify-acceptance <feature> - Verify all acceptance criteria before completion

     P1 Commands (high value):
     3. /new-feature <name> <desc> - Bootstrap feature work item with user-story.md, design.md, task.md
     4. /rag-pipeline <query> - Test RAG pipeline end-to-end with debug output
     5. /ingest-test <path-or-url> - Quick test document ingestion

     P2 Commands (convenience):
     6. /review-design <feature> - Review design against architecture.md and standards
     7. /genai-sync - Update genai-specs rules from GitHub

     Phase 3: Custom Skills (5 minutes)

     P0 Skill:
     1. tdd-workflow - Auto-activates when writing tests/implementing features

     P1 Skills:
     2. rag-architecture - Provides RAG/CAG expertise when designing retrieval workflows
     3. genai-specs-docs - Ensures documentation follows standards (EARS format, etc.)

     Phase 4: Documentation & Testing (5 minutes)

     - Update .claude/DEVELOPMENT.md with command reference
     - Test each command with example usage
     - Verify skills activate appropriately
     - Commit changes

     Key Features

     Slash Commands provide:
     - Workflow automation (feature creation, verification)
     - Debug tools (RAG pipeline testing, ingestion testing)
     - Standards enforcement (design review, acceptance verification)
     - TDD guidance (structured Red→Green→Refactor cycles)

     Skills provide:
     - Contextual domain expertise (RAG patterns, TDD practices)
     - Automatic activation based on context
     - Documentation standards enforcement
     - Test template generation

     Benefits

     - Time Savings: ~30-40 min per feature (automated setup, verification)
     - Consistency: All features follow same genai-specs structure
     - Quality: Enforce TDD and documentation standards automatically
     - Debugging: Faster RAG troubleshooting with /rag-pipeline
     - Onboarding: New developers learn standards through commands/skills

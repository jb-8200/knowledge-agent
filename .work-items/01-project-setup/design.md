# Design: Project Setup

## Objective

Establish a reproducible Python development environment for the knowledge-base agent with all necessary dependencies, configuration management, and directory structure.

## Technical Design

### System Architecture

The project follows a standard Python application structure:
- Backend API server (FastAPI)
- Document ingestion pipeline (LangChain + Firecrawl)
- Vector storage (Qdrant)
- Frontend (static HTML/CSS/JS)

### Technology Stack

- **Python 3.10+**: Core runtime
- **LangChain/LangGraph**: LLM orchestration and agent framework
- **Firecrawl**: Web content extraction
- **Qdrant**: Vector database
- **FastAPI + Uvicorn**: API server
- **sentence-transformers**: Embedding generation
- **python-dotenv**: Environment variable management

## Key Changes

### 3.1 Directory Structure

```
knowledge-agent/
├── .work-items/          # Feature-based work items (genai-specs format)
├── rules/                # Core process and standards (genai-specs)
├── .claude/              # Claude Code configuration and hooks
│   ├── settings.json
│   └── hooks/
├── app/                  # FastAPI backend application
├── ingestion/            # Document parsing and indexing modules
├── frontend/             # Static HTML/CSS/JS files
├── tests/                # Unit and integration tests
├── evals/                # Evaluation harness
│   └── golden-queries.yaml
├── docs/                 # Architecture and decision docs
├── scripts/              # Utility scripts
├── requirements.txt      # Python dependencies
├── .env                  # Environment variables (not committed)
├── .gitignore
└── README.md
```

### 3.2 Dependency Management

**Core Dependencies** (requirements.txt):
```
langchain>=0.1.0
langgraph>=0.0.20
firecrawl-py>=0.0.5
qdrant-client>=1.7.0
fastapi>=0.109.0
uvicorn[standard]>=0.27.0
python-dotenv>=1.0.0
sentence-transformers>=2.2.2
tavily-python>=0.2.0
tenacity>=8.2.0
pdfplumber>=0.10.0
python-docx>=1.1.0
markdown>=3.5.0
```

**Development Dependencies**:
```
pytest>=7.4.0
pytest-asyncio>=0.21.0
black>=23.0.0
ruff>=0.1.0
mypy>=1.8.0
```

### 3.3 Environment Configuration

**.env Template**:
```bash
# LLM Provider
LLM_PROVIDER=local  # or 'openai', 'anthropic', 'google'
MODEL_PROVIDER_API_KEY=your_api_key_here

# Embedding Model
EMBEDDING_MODEL=sentence-transformers/all-MiniLM-L6-v2

# Vector Store
QDRANT_URL=http://localhost:6333
QDRANT_API_KEY=  # Optional for Qdrant Cloud

# Web Search
SEARCH_API_KEY=your_tavily_key_here

# Firecrawl
FIRECRAWL_API_KEY=your_firecrawl_key_here

# YouTube (for thumbnails)
YOUTUBE_API_KEY=your_youtube_key_here

# Application
DEBUG=true
LOG_LEVEL=INFO
```

### 3.4 Git Configuration

**.gitignore**:
```
# Python
__pycache__/
*.py[cod]
*$py.class
venv/
env/
.venv/

# Environment
.env
.env.local

# IDEs
.vscode/
.idea/
*.swp

# Artifacts
artifacts/
*.log

# OS
.DS_Store
Thumbs.db

# Frontend
node_modules/
dist/
```

## Alternatives Considered

1. **Poetry vs pip**: Chose pip + requirements.txt for simplicity; Poetry adds overhead for this project size
2. **Docker-first development**: Deferred to deployment phase; local venv is sufficient for development
3. **Monorepo vs separate frontend**: Chose monorepo for easier local development

## Out of Scope

- Containerization (covered in deployment feature)
- CI/CD pipeline setup
- Production database configuration
- Authentication/authorization setup

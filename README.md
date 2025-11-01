# Knowledge Agent

A **knowledge-base agent** combining **RAG (truth)** + **CAG (intelligence)** for accurate, cited answers from both internal documents and external web sources.

## 🎯 Overview

This agent provides:

- **RAG (Retrieval-Augmented Generation)**: Internal document search using vector embeddings
- **CAG (Contextual-Augmented Generation)**: External web search when internal knowledge gaps exist
- **Citation-backed answers**: All responses include source references
- **Multi-format ingestion**: PDF, Word, Markdown, and web URLs

## 🏗️ Architecture

```
User Query → RAG Retriever (Qdrant) → Synthesizer (decides if external needed)
                                            ↓
                          Web Search (Tavily) → Firecrawl → Summarizer
                                            ↓
                          Critic (merge internal + external) → Answer + Citations
```

## 🔧 Technology Stack

- **Agent Framework**: LangChain
- **Vector Database**: Qdrant
- **Embeddings**: Sentence Transformers
- **Web Extraction**: Firecrawl
- **Web Search**: Tavily
- **Backend API**: FastAPI + Uvicorn
- **Frontend**: HTML/CSS/JavaScript

## 🚀 Quick Start

### Prerequisites

- Python 3.10 or higher
- pip (Python package manager)

### Installation

1. **Clone the repository**:

   ```bash
   git clone https://github.com/jb-8200/knowledge-agent.git
   cd knowledge-agent
   ```

2. **Create and activate virtual environment**:

   ```bash
   python3 -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**:

   ```bash
   pip install -r requirements.txt
   ```

4. **Configure environment variables**:

   ```bash
   cp .env.template .env
   # Edit .env with your API keys:
   # - MODEL_PROVIDER_API_KEY (OpenAI, Anthropic, etc.)
   # - QDRANT_URL (or use local mode)
   # - TAVILY_API_KEY (for web search)
   # - YOUTUBE_API_KEY (optional, for video features)
   ```

### Running Tests

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=app

# Run specific test file
pytest tests/test_setup.py -v
```

### Development

```bash
# Activate virtual environment
source venv/bin/activate

# Run type checking
mypy app/

# Run linting and formatting
ruff check .
ruff format .
```

## 📂 Project Structure

```
knowledge-agent/
├── app/                    # Application source code
├── tests/                  # Test suite
├── .work-items/            # Feature-based work items
├── docs/                   # Documentation
├── rules/                  # Development process & standards
├── .claude/                # Claude Code configuration
├── requirements.txt        # Python dependencies
├── .env.template           # Environment variables template
└── README.md               # This file
```

## 📖 Documentation

- **[Architecture](docs/architecture.md)**: System design and RAG+CAG approach
- **[Project Structure](PROJECT_STRUCTURE.md)**: Directory layout and navigation
- **[Development Guide](.claude/DEVELOPMENT.md)**: Development workflow and TDD practices

## 🤝 Contributing

This project follows **genai-specs** workflow:

1. **User Story** → Define user value
2. **Design** → Technical approach
3. **Tasks** → TDD implementation steps
4. **Verification** → Test coverage and acceptance criteria

See [.claude/DEVELOPMENT.md](.claude/DEVELOPMENT.md) for detailed development practices.

## 📝 License

Copyright (c) 2025. All rights reserved.

## 🔗 Links

- **Repository**: [https://github.com/jb-8200/knowledge-agent](https://github.com/jb-8200/knowledge-agent)
- **Issues**: [https://github.com/jb-8200/knowledge-agent/issues](https://github.com/jb-8200/knowledge-agent/issues)

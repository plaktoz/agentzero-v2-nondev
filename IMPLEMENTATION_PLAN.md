# Implementation Plan: Unified Content Agent System (Non-Dev)

## Project Status: Foundation Phase (Week 1-2)

### ✅ Completed

1. **Project Structure**
   - Created directory structure for all components
   - Set up Python package structure with `__init__.py`
   - Organized into logical modules (core, agents, providers, storage, quality, cli)

2. **Configuration Management**
   - Created `config/default.yaml` with system settings
   - Created `config/workflows.yaml` with content type workflows
   - Defined provider configurations (Claude, OpenAI, Gemini)
   - Set up quality scoring weights and thresholds

3. **Technology Stack**
   - Selected Python 3.10+ as primary language
   - Created `requirements.txt` with all dependencies
   - Created `pyproject.toml` for modern Python packaging
   - Configured development tools (black, ruff, mypy, pytest)

4. **Provider Abstraction**
   - Implemented `BaseProvider` abstract class
   - Implemented `ClaudeProvider` with Anthropic API integration
   - Defined `Message` and `ProviderResponse` data structures
   - Added capability detection and token estimation

5. **Document Storage**
   - Implemented `DocumentStorage` class with file-based storage
   - Added document versioning support
   - Created metadata management system
   - Implemented status tracking (draft, review, approved, published)

6. **Base Agent Framework**
   - Implemented `BaseAgent` class
   - Created `AgentContext` and `AgentResult` data structures
   - Added system prompt building
   - Implemented message construction and response processing

### 🚧 In Progress

None currently - ready to start next phase

### 📋 Next Steps (Week 2-4)

#### Phase 1A: Core Orchestration (Week 2)

1. **Coordinator Agent** (`src/core/coordinator.py`)
   - Main orchestrator for all agent activities
   - Request parsing and workflow selection
   - Agent spawning and lifecycle management
   - Result aggregation and error handling

2. **Router** (`src/core/router.py`)
   - Workflow selection based on content type
   - Agent selection for each workflow step
   - Dependency management between steps

3. **Specialized Agents** (`src/agents/`)
   - `researcher.py` - Research and source gathering
   - `writer.py` - Content creation
   - `editor.py` - Content polishing

#### Phase 1B: Quality & CLI (Week 3-4)

4. **Quality Review** (`src/quality/reviewer.py`)
   - Quality scoring implementation
   - Multi-dimensional evaluation (accuracy, clarity, etc.)
   - Threshold checking

5. **CLI Interface** (`src/cli/main.py`)
   - Typer-based CLI with commands:
     - `init` - Initialize system
     - `request` - Submit content request
     - `status` - Check task status
     - `list` - List documents
     - `show` - Show document content
     - `approve` - Approve content

6. **Token Tracking** (`src/core/token_tracker.py`)
   - Track token usage per task
   - Budget enforcement
   - Cost estimation

### 📊 Success Criteria for MVP

- [ ] Can create simple blog post (1000 words) end-to-end
- [ ] Context persists across restarts
- [ ] Token usage tracked and reported
- [ ] Quality score calculated and displayed
- [ ] CLI commands work for basic workflow
- [ ] Single provider (Claude) fully functional

### 🎯 MVP Scope (3-4 months)

**What's Included:**
- 5 concurrent agents maximum
- Single provider (Claude)
- Basic workflows (blog post, research report)
- File-based document storage
- Simple quality review
- CLI interface only
- Basic token tracking

**What's Deferred:**
- Multi-provider support (Phase 2)
- Advanced quality scoring (Phase 2)
- Knowledge base with search (Phase 2)
- Fact verification system (Phase 2)
- Dashboard interface (Phase 3)
- 20+ concurrent agents (Phase 3)

### 📝 Implementation Notes

**Design Decisions:**
1. **File-based storage** - Simple, version-controllable, no database complexity
2. **Async/await** - All I/O operations are async for better performance
3. **Provider abstraction** - Easy to add new LLM providers later
4. **Workflow-driven** - Content types map to specific workflows
5. **Quality gates** - Systematic review before approval

**Key Files:**
- `src/core/coordinator.py` - Main orchestration logic
- `src/core/router.py` - Workflow routing
- `src/storage/documents.py` - Document management
- `src/providers/claude.py` - Claude integration
- `src/cli/main.py` - User interface

### 🔧 Development Commands

```bash
# Install dependencies
pip install -e ".[dev]"

# Run tests
pytest

# Format code
black src/ tests/

# Lint code
ruff check src/ tests/

# Type check
mypy src/

# Run CLI
python -m ucas --help
```

### 📚 Documentation Needed

1. **User Guide** - How to use the system
2. **Developer Guide** - How to extend the system
3. **API Reference** - Code documentation
4. **Workflow Guide** - How workflows work
5. **Configuration Guide** - How to configure the system

### 🚀 Next Immediate Actions

1. Implement `Coordinator` class
2. Implement `Router` class
3. Create specialized agent classes (Researcher, Writer, Editor)
4. Build basic CLI with Typer
5. Add integration tests
6. Write user documentation

### 📈 Progress Tracking

**Week 1-2:** Foundation ✅ (100% complete)
- Project structure
- Configuration
- Base classes
- Provider integration
- Document storage

**Week 3-4:** Core Orchestration (0% complete)
- Coordinator
- Router
- Specialized agents

**Week 5-6:** Quality & CLI (0% complete)
- Quality review
- CLI interface
- Token tracking

**Week 7-8:** Testing & Documentation (0% complete)
- Integration tests
- User documentation
- Example workflows

---

**Last Updated:** 2026-10-18
**Status:** Foundation Complete, Ready for Core Orchestration Phase

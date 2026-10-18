# Unified Content Agent System (Non-Dev)

A multi-agent system for content creation, research, and knowledge work with context persistence and quality assurance.

## Overview

This system coordinates AI agents to produce high-quality content through structured workflows, systematic review, and persistent context management.

### Key Features

- **Context Persistence**: All research and drafts survive crashes
- **Multi-Provider Support**: ✅ Claude, GPT-4, and Gemini fully implemented with easy switching
- **Quality Assurance**: Systematic fact-checking and review
- **Knowledge Base**: Reusable content library to avoid duplication
- **Structured Workflows**: Domain-specific workflows for different content types
- **Update Management**: Built-in update, rollback, and uninstall commands

## Quick Start

```bash
# Install dependencies
pip install -r requirements.txt

# Configure API keys
export ANTHROPIC_API_KEY=your_key_here

# Initialize system
python -m ucas init

# Create content
python -m ucas request "Write blog post on AI trends"

# Monitor progress
python -m ucas watch
```

## Architecture

```
┌─────────────────────────────────────────┐
│         Human Interface (CLI)            │
└─────────────────────────────────────────┘
                    ↓
┌─────────────────────────────────────────┐
│      Coordinator & Router                │
└─────────────────────────────────────────┘
                    ↓
┌─────────────────────────────────────────┐
│  Agents (Researcher, Writer, Editor)     │
└─────────────────────────────────────────┘
                    ↓
┌─────────────────────────────────────────┐
│  Quality Review & Fact Checking          │
└─────────────────────────────────────────┘
                    ↓
┌─────────────────────────────────────────┐
│  Document Storage & Knowledge Base       │
└─────────────────────────────────────────┘
```

## Project Structure

```
ucas/
├── src/
│   ├── core/
│   │   ├── coordinator.py      # Main orchestrator
│   │   ├── router.py            # Workflow routing
│   │   └── agent.py             # Base agent class
│   ├── agents/
│   │   ├── researcher.py        # Research agent
│   │   ├── writer.py            # Content writer
│   │   └── editor.py            # Content editor
│   ├── providers/
│   │   ├── base.py              # Provider interface
│   │   ├── claude.py            # Claude provider
│   │   ├── openai.py            # OpenAI provider
│   │   └── gemini.py            # Gemini provider
│   ├── storage/
│   │   ├── documents.py         # Document storage
│   │   └── knowledge_base.py    # Knowledge base
│   ├── quality/
│   │   ├── reviewer.py          # Quality review
│   │   └── fact_checker.py      # Fact verification
│   └── cli/
│       └── main.py              # CLI interface
├── config/
│   ├── default.yaml             # Default configuration
│   └── workflows.yaml           # Workflow definitions
├── tests/
├── docs/
├── requirements.txt
└── setup.py
```

## Configuration

### Environment Variables

```bash
# At least one provider required
ANTHROPIC_API_KEY=your_claude_key    # For Claude (Anthropic)
OPENAI_API_KEY=your_openai_key       # For GPT-4 (OpenAI)
GOOGLE_API_KEY=your_gemini_key       # For Gemini (Google)
```

### Configuration File (config/default.yaml)

```yaml
system:
  max_agents: 5
  default_provider: claude
  
providers:
  claude:
    model: claude-3-5-sonnet-20241022
    max_tokens: 4096
    
quality:
  minimum_score: 8.0
  fact_check_required: true
  
storage:
  documents_path: ./documents
  knowledge_base_path: ./knowledge_base
```

## Usage Examples

### Simple Content Request

```python
from ucas import Coordinator

coordinator = Coordinator()
result = coordinator.request("Write 1000-word article on AI safety")
print(result.content)
```

### Research Report

```python
coordinator = Coordinator()
result = coordinator.request(
    "Research report on quantum computing trends",
    content_type="research_report",
    min_sources=15
)
```

### Blog Post with SEO

```python
result = coordinator.request(
    "Blog post: 10 productivity tips",
    content_type="blog_post",
    seo_optimize=True,
    target_keywords=["productivity", "AI tools"]
)
```

## Development Roadmap

### Phase 1: MVP (Complete ✅)
- [x] Project structure
- [x] Document storage with versioning
- [x] Multi-provider support (Claude, OpenAI, Gemini)
- [x] Provider factory and configuration
- [x] Coordinator and router
- [x] Specialized agents (Researcher, Writer, Editor)
- [x] CLI interface with 11 commands
- [x] Update/uninstall/rollback commands

### Phase 2: Enhancement (In Progress 🚧)
- [x] Multi-provider support (Claude, GPT-4, Gemini)
- [x] Specialized agents
- [ ] Knowledge base with search
- [ ] Fact verification
- [ ] Advanced quality scoring
- [ ] Token tracking and budgets

### Phase 3: Scale (4-6 months)
- [ ] 20+ concurrent agents
- [ ] Advanced monitoring
- [ ] Multi-project support
- [ ] Dashboard interface

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md) for development guidelines.

## License

MIT License - See [LICENSE](LICENSE) for details.

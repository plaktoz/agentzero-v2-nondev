# Quick Start Guide

Get started with the Unified Content Agent System in 5 minutes.

## Prerequisites

- Python 3.10 or higher
- Anthropic API key (Claude)

## Installation

### 1. Clone and Setup

```bash
cd poc-multi-agent-system-v2

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -e .
```

### 2. Configure API Key

```bash
# Copy example environment file
cp .env.example .env

# Edit .env and add your API key
export ANTHROPIC_API_KEY=your_key_here
```

### 3. Initialize System

```bash
python -m ucas init
```

## Basic Usage

### Create Your First Content

```bash
# Simple blog post
python -m ucas request "Write a blog post about AI in healthcare"

# With specific word count
python -m ucas request "Write about quantum computing" --words 1500

# Specific content type
python -m ucas request "Research report on climate change" --type research_report
```

### Check Status

```bash
# Get request ID from previous command output
python -m ucas status <request-id>
```

### View Content

```bash
python -m ucas show <request-id>
```

### List All Documents

```bash
# List all
python -m ucas list

# Filter by status
python -m ucas list --status draft

# Filter by type
python -m ucas list --type blog_post
```

### Approve Content

```bash
python -m ucas approve <request-id>
```

## Programmatic Usage

```python
import asyncio
from src.core.coordinator import Coordinator
from src.providers.claude import ClaudeProvider
from src.storage.documents import DocumentStorage

async def create_content():
    # Initialize
    provider_config = {
        "model": "claude-3-5-sonnet-20241022",
        "max_tokens": 4096,
        "temperature": 0.7,
        "api_key_env": "ANTHROPIC_API_KEY"
    }
    
    provider = ClaudeProvider(provider_config)
    storage = DocumentStorage("./documents")
    coordinator = Coordinator(provider, storage, {})
    
    # Create content
    request_id = await coordinator.request(
        description="Write about AI trends",
        content_type="blog_post",
        target_words=1000
    )
    
    print(f"Request ID: {request_id}")
    
    # Check status
    status = await coordinator.get_status(request_id)
    print(f"Status: {status['status']}")
    
    # Load document when complete
    if status['status'] == 'completed':
        content, metadata = await storage.load_document(request_id)
        print(f"Content: {content[:200]}...")

asyncio.run(create_content())
```

## Available Workflows

```bash
# See all available workflows
python -m ucas workflows
```

Current workflows:
- **blog_post**: Engaging blog content (1000 words)
- **research_report**: In-depth research with citations (3000 words)
- **technical_docs**: Clear technical documentation
- **marketing_copy**: Persuasive marketing content
- **social_media**: Short-form social content

## Configuration

Edit `config/default.yaml` to customize:

```yaml
system:
  max_agents: 5
  default_provider: claude

providers:
  claude:
    model: claude-3-5-sonnet-20241022
    max_tokens: 4096
    temperature: 0.7

quality:
  minimum_score: 8.0
  fact_check_required: true
```

## Troubleshooting

### API Key Not Found

```bash
# Make sure environment variable is set
echo $ANTHROPIC_API_KEY

# Or set it directly
export ANTHROPIC_API_KEY=your_key_here
```

### Import Errors

```bash
# Reinstall in development mode
pip install -e .
```

### Permission Errors

```bash
# Make sure directories exist
python -m ucas init
```

## Next Steps

1. **Try the example**: `python examples/basic_usage.py`
2. **Read the docs**: See `README.md` for detailed information
3. **Customize workflows**: Edit `config/workflows.yaml`
4. **Add more providers**: See Phase 2 roadmap

## Getting Help

- Check `README.md` for detailed documentation
- Review `IMPLEMENTATION_PLAN.md` for architecture details
- See `examples/` for more usage examples

## What's Next?

Current MVP includes:
- ✅ Single provider (Claude)
- ✅ 5 concurrent agents
- ✅ Basic workflows
- ✅ CLI interface

Coming in Phase 2 (3-4 months):
- Multi-provider support (OpenAI, Gemini)
- Advanced quality scoring
- Knowledge base with search
- Fact verification system
- Dashboard interface

Coming in Phase 3 (4-6 months):
- 20+ concurrent agents
- Advanced monitoring
- Multi-project support
- Enterprise features

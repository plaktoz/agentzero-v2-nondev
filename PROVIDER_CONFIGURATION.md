# Provider Configuration Guide

This guide shows how to configure and switch between different LLM providers (Claude, GPT-4, Gemini).

## Overview

The system supports multiple LLM providers through an adapter pattern. You can:
- Use a single provider (MVP default: Claude)
- Switch between providers at runtime
- Configure different providers for different agent types

---

## Provider Setup

### 1. Claude (Anthropic) - Default

**Get API Key:**
1. Sign up at https://console.anthropic.com/
2. Create an API key
3. Copy the key (starts with `sk-ant-`)

**Configure:**

```bash
# Set environment variable
export ANTHROPIC_API_KEY=sk-ant-api03-...

# Or add to .env file
echo "ANTHROPIC_API_KEY=sk-ant-api03-..." >> .env
```

**Configuration in `config/default.yaml`:**

```yaml
providers:
  claude:
    enabled: true
    model: "claude-3-5-sonnet-20241022"
    max_tokens: 4096
    temperature: 0.7
    api_key_env: "ANTHROPIC_API_KEY"
```

**Available Models:**
- `claude-3-5-sonnet-20241022` (recommended, 200K context)
- `claude-3-opus-20240229` (most capable, 200K context)
- `claude-3-sonnet-20240229` (balanced, 200K context)
- `claude-3-haiku-20240307` (fastest, 200K context)

---

### 2. GPT-4 (OpenAI) - Available Now

**Get API Key:**
1. Sign up at https://platform.openai.com/
2. Create an API key
3. Copy the key (starts with `sk-`)

**Configure:**

```bash
# Set environment variable
export OPENAI_API_KEY=sk-...

# Or add to .env file
echo "OPENAI_API_KEY=sk-..." >> .env
```

**Configuration in `config/default.yaml`:**

```yaml
providers:
  openai:
    enabled: true
    model: "gpt-4-turbo"
    max_tokens: 4096
    temperature: 0.7
    api_key_env: "OPENAI_API_KEY"
```

**Available Models:**
- `gpt-4-turbo` (recommended, 128K context)
- `gpt-4` (original, 8K context)
- `gpt-4-32k` (extended context)
- `gpt-3.5-turbo` (faster, cheaper, 16K context)

**Implementation Status:** ✅ Available Now

---

### 3. Gemini (Google) - Available Now

**Get API Key:**
1. Go to https://makersuite.google.com/app/apikey
2. Create an API key
3. Copy the key

**Configure:**

```bash
# Set environment variable
export GOOGLE_API_KEY=AIza...

# Or add to .env file
echo "GOOGLE_API_KEY=AIza..." >> .env
```

**Configuration in `config/default.yaml`:**

```yaml
providers:
  gemini:
    enabled: true
    model: "gemini-1.5-pro"
    max_tokens: 4096
    temperature: 0.7
    api_key_env: "GOOGLE_API_KEY"
```

**Available Models:**
- `gemini-1.5-pro` (recommended, 1M context!)
- `gemini-1.5-flash` (faster, 1M context)
- `gemini-pro` (original, 32K context)

**Implementation Status:** 🚧 Coming in Phase 2

---

## Switching Providers

### Method 1: Change Default Provider

Edit `config/default.yaml`:

```yaml
system:
  default_provider: "claude"  # or "openai" or "gemini"
```

### Method 2: Per-Agent Configuration (Phase 2)

Configure different providers for different agent types:

```yaml
agents:
  researcher:
    provider: "gemini"  # Use Gemini for research (1M context)
    model: "gemini-1.5-pro"
    
  writer:
    provider: "claude"  # Use Claude for writing
    model: "claude-3-5-sonnet-20241022"
    
  editor:
    provider: "openai"  # Use GPT-4 for editing
    model: "gpt-4-turbo"
```

### Method 3: Runtime Selection (Phase 2)

```python
from src.core.coordinator import Coordinator
from src.providers.claude import ClaudeProvider
from src.providers.openai import OpenAIProvider  # Phase 2
from src.providers.gemini import GeminiProvider  # Phase 2

# Use Claude
claude_provider = ClaudeProvider(config)
coordinator = Coordinator(claude_provider, storage, config)

# Or use GPT-4
openai_provider = OpenAIProvider(config)
coordinator = Coordinator(openai_provider, storage, config)

# Or use Gemini
gemini_provider = GeminiProvider(config)
coordinator = Coordinator(gemini_provider, storage, config)
```

---

## Provider Comparison

| Feature | Claude | GPT-4 | Gemini |
|---------|--------|-------|--------|
| **Context Window** | 200K tokens | 128K tokens | 1M tokens |
| **Best For** | Long-form writing, analysis | Creative writing, general | Research, long context |
| **Speed** | Fast | Medium | Fast |
| **Cost (per 1M tokens)** | $15 input, $75 output | $30 input, $60 output | $7 input, $21 output |
| **Strengths** | Technical accuracy, clarity | Creativity, versatility | Massive context, research |
| **Weaknesses** | Less creative | Shorter context | Newer, less tested |
| **Status** | ✅ Available | ✅ Available | ✅ Available |

---

## Cost Optimization

### Strategy 1: Use Cheaper Models for Simple Tasks

```yaml
agents:
  researcher:
    provider: "gemini"
    model: "gemini-1.5-flash"  # Cheaper, still 1M context
    
  writer:
    provider: "claude"
    model: "claude-3-haiku-20240307"  # Cheaper, faster
    
  editor:
    provider: "openai"
    model: "gpt-3.5-turbo"  # Much cheaper
```

### Strategy 2: Set Token Budgets

```yaml
token_budget:
  daily_limit: 100000  # 100K tokens per day
  per_task_limit: 10000  # 10K tokens per task
  
  alert_thresholds:
    - 0.8  # Alert at 80%
    - 0.9  # Alert at 90%
    - 0.95 # Alert at 95%
```

### Strategy 3: Provider Selection by Task Type

```yaml
# Use Gemini for research (cheap, huge context)
research_report:
  preferred_provider: "gemini"
  
# Use Claude for technical writing (accuracy)
technical_docs:
  preferred_provider: "claude"
  
# Use GPT-4 for creative content
blog_post:
  preferred_provider: "openai"
```

---

## Complete Configuration Example

**`.env` file:**

```bash
# All providers configured
ANTHROPIC_API_KEY=sk-ant-api03-...
OPENAI_API_KEY=sk-...
GOOGLE_API_KEY=AIza...
```

**`config/default.yaml`:**

```yaml
system:
  name: "ucas"
  version: "0.1.0"
  max_agents: 5
  default_provider: "claude"

providers:
  claude:
    enabled: true
    model: "claude-3-5-sonnet-20241022"
    max_tokens: 4096
    temperature: 0.7
    api_key_env: "ANTHROPIC_API_KEY"
    
  openai:
    enabled: true
    model: "gpt-4-turbo"
    max_tokens: 4096
    temperature: 0.7
    api_key_env: "OPENAI_API_KEY"
    
  gemini:
    enabled: true
    model: "gemini-1.5-pro"
    max_tokens: 4096
    temperature: 0.7
    api_key_env: "GOOGLE_API_KEY"

# Per-agent provider configuration (Phase 2)
agents:
  researcher:
    provider: "gemini"  # Best for research with 1M context
    model: "gemini-1.5-pro"
    max_tokens: 8192
    
  writer:
    provider: "claude"  # Best for writing quality
    model: "claude-3-5-sonnet-20241022"
    max_tokens: 4096
    
  editor:
    provider: "openai"  # Good for polishing
    model: "gpt-4-turbo"
    max_tokens: 4096

token_budget:
  daily_limit: 100000
  per_task_limit: 10000
  alert_thresholds: [0.8, 0.9, 0.95]
```

---

## Testing Provider Configuration

### Test Claude (Current MVP)

```bash
# Set API key
export ANTHROPIC_API_KEY=your_key_here

# Test
python -m ucas request "Write a short test post"
```

### Test OpenAI (Phase 2)

```bash
# Set API key
export OPENAI_API_KEY=your_key_here

# Update config to use OpenAI
# Edit config/default.yaml: default_provider: "openai"

# Test
python -m ucas request "Write a short test post"
```

### Test Gemini (Phase 2)

```bash
# Set API key
export GOOGLE_API_KEY=your_key_here

# Update config to use Gemini
# Edit config/default.yaml: default_provider: "gemini"

# Test
python -m ucas request "Write a short test post"
```

---

## Troubleshooting

### API Key Not Found

```bash
# Check if environment variable is set
echo $ANTHROPIC_API_KEY
echo $OPENAI_API_KEY
echo $GOOGLE_API_KEY

# Set if missing
export ANTHROPIC_API_KEY=your_key_here
```

### Provider Not Enabled

Check `config/default.yaml`:

```yaml
providers:
  claude:
    enabled: true  # Must be true
```

### Rate Limits

If you hit rate limits:

1. **Reduce concurrent agents:**
   ```yaml
   system:
     max_agents: 3  # Reduce from 5
   ```

2. **Add delays between requests:**
   ```yaml
   providers:
     claude:
       rate_limit_delay: 1.0  # 1 second delay
   ```

3. **Use cheaper models:**
   ```yaml
   providers:
     claude:
       model: "claude-3-haiku-20240307"  # Faster, cheaper
   ```

---

## Recommendations

### For MVP (Current)

**Use Claude:**
- ✅ Available now
- ✅ Great for all content types
- ✅ 200K context window
- ✅ Good balance of quality and cost

```yaml
system:
  default_provider: "claude"

providers:
  claude:
    enabled: true
    model: "claude-3-5-sonnet-20241022"
```

### For Phase 2 (Multi-Provider)

**Use provider strengths:**
- **Gemini** for research (1M context, cheap)
- **Claude** for writing (quality, accuracy)
- **GPT-4** for creative content (versatility)

```yaml
agents:
  researcher:
    provider: "gemini"
  writer:
    provider: "claude"
  editor:
    provider: "openai"
```

---

## Next Steps

1. **✅ Complete:** All three providers (Claude, OpenAI, Gemini) implemented
2. **Phase 2:** Add automatic provider selection based on task type
3. **Phase 3:** Add cost optimization and provider fallback
4. **Phase 4:** Add per-agent provider configuration

---

## Getting Help

- **Claude API Docs:** https://docs.anthropic.com/
- **OpenAI API Docs:** https://platform.openai.com/docs/
- **Gemini API Docs:** https://ai.google.dev/docs/

For system-specific issues, see `README.md` or `QUICKSTART.md`.

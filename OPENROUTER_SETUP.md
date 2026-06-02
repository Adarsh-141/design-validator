# OpenRouter Setup Guide

## What is OpenRouter?

OpenRouter provides access to **dozens of LLM models** through a single API:
- Claude (Anthropic)
- GPT-4 (OpenAI)
- Mistral
- Llama
- And many more...

**Key Benefits:**
- ✅ **Fast**: 2-5 second responses
- ✅ **Cheap**: Many free models available
- ✅ **Flexible**: Switch models without downloading
- ✅ **Easy**: Single API key for all models

---

## Setup (5 minutes)

### Step 1: Get OpenRouter API Key

1. Go to **https://openrouter.ai**
2. Sign up (free account)
3. Go to **API Keys** page
4. Copy your API key: `sk-or-...`

### Step 2: Set Environment Variable

**PowerShell:**
```powershell
$env:OPENROUTER_API_KEY="sk-or-your-key-here"
```

**Windows CMD:**
```cmd
set OPENROUTER_API_KEY=sk-or-your-key-here
```

**Permanent (Windows):**
```powershell
# Run as Administrator
[Environment]::SetEnvironmentVariable("OPENROUTER_API_KEY", "sk-or-your-key-here", "User")
```

### Step 3: Run the Validator

**Using default GPT-3.5 Turbo:**
```powershell
python -m src.main `
  --design "Your design description..." `
  --output results/report.json `
  --verbose
```

**Using a specific model:**
```powershell
python -m src.main `
  --design "..." `
  --openrouter-model "anthropic/claude-3-haiku" `
  --verbose
```

---

## Recommended Models

### Fast & Cheap 💰 (Recommended for testing)
```powershell
--openrouter-model "gpt-3.5-turbo"
```
- **Speed**: 2-5 seconds
- **Cost**: ~$0.002 per design run
- **Quality**: Good for basic reasoning

### Best Reasoning ⭐
```powershell
--openrouter-model "anthropic/claude-3-haiku"
```
- **Speed**: 5-10 seconds
- **Cost**: ~$0.004 per design run
- **Quality**: Excellent for complex analysis

---

## Cost Estimation

### Per Design Run
| Model | Tokens | Cost |
|-------|--------|------|
| GPT-3.5 Turbo | ~5,000 | $0.003 |
| Claude Haiku | ~5,000 | $0.004 |
| GPT-4 Turbo | ~5,000 | $0.075 |

**1000 design runs:**
- GPT-3.5: $3.00
- Claude Haiku: $4.00
- GPT-4: $75

---

## All Available Models

Find full list at: https://openrouter.ai/docs/models

Quick reference:
```python
# Fast & cheap
"gpt-3.5-turbo"
"anthropic/claude-3-haiku"

# Better reasoning
"anthropic/claude-3-opus"
"openai/gpt-4-turbo"
```

---

## Using OpenRouter

```powershell
python -m src.main --design "..." --output results/report.json
```

That's it! ✅

---

## Troubleshooting

### "Invalid OpenRouter API key"
- Check you copied the full key from https://openrouter.ai/keys
- Verify environment variable: `echo $env:OPENROUTER_API_KEY`

### "Rate limited"
- You've hit the free tier limit
- Upgrade account or wait for rate limit reset

### "Model not found"
- Check spelling at https://openrouter.ai/docs/models
- Some models may be deprecated

---

## Cost Control

### Option 1: Use Free Models
```powershell
--openrouter-model "mistralai/mistral-7b-instruct:free"
```
Completely free for testing.

### Option 2: Set Monthly Budget
In OpenRouter dashboard → Settings → Budget limits

### Option 3: Monitor Usage
OpenRouter shows live token usage in dashboard

---

## Python API Usage

```python
from src.main import validate_design

# Using OpenRouter
report = validate_design(
    design_input="Your design...",
    openrouter_api_key="sk-or-...",
    openrouter_model="gpt-3.5-turbo",
    output_file="results/report.json",
    verbose=True
)
```

---

## Performance

| Metric | OpenRouter |
|--------|------------|
| Speed | 2-5 sec |
| Setup | 5 min (API key) |
| Cost | Low (~$0.003-0.004 per run) |
| Reliability | High (redundant servers) |
| Models | 50+ options |

---

**Ready to go?** 🚀

1. Get API key: https://openrouter.ai
2. Set environment variable: `$env:OPENROUTER_API_KEY="..."`
3. Run: `python -m src.main --design "..." --output results/report.json`

Enjoy fast design validation! ⚡

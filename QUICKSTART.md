# Quick Start Guide

## 1. Setup (One-time)

```bash
# Install dependencies
pip install -r requirements.txt

# Copy .env template
cp .env.example .env

# Edit .env with your API key
```

## 2. Get OpenRouter API Key

1. Go to https://openrouter.ai
2. Sign up (free)
3. Copy API key from https://openrouter.ai/keys
4. Paste into `.env` file:

```
OPENROUTER_API_KEY=sk-or-your-key-here
```

## 3. Run Validator

### Simplest way:
```powershell
python -m src.main --design "Your design description here"
```

### With custom output file:
```powershell
python -m src.main --design "..." --output my_report.json
```

### With different model:
```powershell
python -m src.main --design "..." --model "anthropic/claude-3-haiku"
```

### Using the script:
```powershell
./validate.ps1 "Your design description"
```

## 4. View Results

Results automatically save to `results/report.json` (default) with:
- ✅ Parsed design entities
- ✅ Domain analyses (materials + electrical)
- ✅ Detected conflicts with severity scores
- ✅ Suggested modifications

---

## Command Shortcuts

| Short | Long | Example |
|-------|------|---------|
| `-d` | `--design` | `-d "Your design"` |
| `-o` | `--output` | `-o report.json` |
| `-m` | `--model` | `-m "anthropic/claude-3-haiku"` |
| `-k` | `--key` | `-k "sk-or-..."` (override .env) |
| `-v` | `--verbose` | Enable debug logs |

---

## Example Designs

```powershell
# Self-healing material
python -m src.main -d "A self-healing conductive material made from a polymer embedded with microcapsules containing a conductive liquid."

# Smart composite
python -m src.main -d "A carbon fiber composite with embedded thermal sensors that adapt stiffness based on temperature."

# Hybrid battery
python -m src.main -d "A solid-state battery with silicon anodes that expand during charging but need mechanical constraint."
```

---

## Troubleshooting

**"Invalid API key"** → Check .env file has your real key
**"ModuleNotFoundError"** → Run `pip install -r requirements.txt`
**"slow execution"** → Try a faster model: `-m "gpt-3.5-turbo"` or `-m "anthropic/claude-3-haiku"`

---

**That's it!** 🚀

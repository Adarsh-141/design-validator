# Design Validator - Multi-Agent Cross-Domain Conflict Detection

A production-quality, multi-agent simulation system that predicts emergent conflicts when designs operate across multiple domains.

## 🎯 Overview

**Problem**: Design decisions optimized for one domain (e.g., Materials Science) often create unintended problems in another domain (e.g., Electrical Engineering).

**Solution**: Multi-agent system using LangGraph + OpenRouter API for fast LLM inference:
1. Extract design entities from natural language
2. Simulate domain-specific behavior independently
3. Detect cross-domain conflicts systematically
4. Suggest design modifications to resolve conflicts

**Example Design**: *"A self-healing conductive material made from a polymer embedded with microcapsules containing a conductive liquid. When cracked, capsules rupture, liquid bridges the gap, restoring conductivity."*

**Emergent Conflict**: *"Smaller capsules rupture reliably BUT create high-resistance bridges. Larger capsules provide good conductivity BUT fail to rupture under normal loads."*

## 📋 Architecture

### Components

```
Design Input (Natural Language)
    ↓
┌─── Parser Agent ────────────────────────┐
│ Extract: material, mechanism, failures  │
└─────────────────┬──────────────────────┘
                  ↓
┌────────────────────────────────────────┐
│ Materials Analysis                     │
└────────────────┬───────────────────────┘
  electrical analysis 
                 ↓
┌─── Conflict Detector Agent ─────────────┐
│ Find domain interactions and conflicts  │
└─────────────────┬──────────────────────┘
                  ↓
            Conflicts Found?
           ↙              ↘
         YES              NO
          ↓               ↓
    Modification Agent  Format Output
          ↓               ↓
          └───────┬───────┘
                  ↓
          JSON Validation Report
```

### Agent Specifications

| Agent | Responsibility | Input | Output |
|-------|----------------|-------|--------|
| **Parser** | Extract structured entities | Design description (string) | Parsed entities dict |
| **Materials** | Analyze mechanical properties | Parsed design | Mechanical analysis |
| **Electrical** | Analyze electrical properties | Parsed design | Electrical analysis |
| **Conflict Detector** | Find cross-domain conflicts | Both domain analyses | List of conflicts |
| **Modification** | Generate design solutions | Conflicts + design | Suggested modifications |

### State Management

All agents operate on a single `DesignValidationState` TypedDict with immutable transitions:

```python
DesignValidationState = {
    "design_input": str,
    "parsed_design": ParsedDesignEntity,
    "materials_analysis": MechanicalAnalysis,
    "electrical_analysis": ElectricalAnalysis,
    "detected_conflicts": List[DomainConflict],
    "suggested_modifications": List[DesignModification],
    "validation_report": dict,
    "execution_metadata": ExecutionMetadata
}
```

## 🚀 Quick Start

### 1. Install Dependencies

```bash
# Create virtual environment (recommended)
python -m venv venv
source venv/Scripts/activate  # Windows
# or
source venv/bin/activate       # Linux/Mac

# Install packages
pip install -r requirements.txt
```

### 2. Get OpenRouter API Key

1. Go to https://openrouter.ai
2. Sign up (free account)
3. Get your API key from https://openrouter.ai/keys

### 3. Run the Validator

```bash
# Set API key (PowerShell)
$env:OPENROUTER_API_KEY="sk-or-your-key-here"

# Command-line interface
python -m src.main `
  --design "A self-healing conductive material made from a polymer embedded with microcapsules containing a conductive liquid. When cracked, capsules rupture, liquid bridges the gap, restoring conductivity." `
  --output results/output.json `
  --verbose

# Or use the Python API
from src.main import validate_design

report = validate_design(
    design_input="Your design description...",
    openrouter_api_key="sk-or-your-key",
    output_file="results/output.json",
    verbose=True
)

print(f"Status: {report['validation_status']}")
print(f"Conflicts found: {len(report['predicted_conflicts'])}")
```

## 📊 Output Format

### JSON Report Structure

```json
{
  "metadata": {
    "timestamp": "2026-06-02T14:23:45Z",
    "model_used": "mistral:7b",
    "total_execution_time_seconds": 45.3,
    "tokens_used": 5234
  },
  "parsed_design": {
    "material_type": "polymer",
    "active_mechanism": "microcapsules + conductive liquid",
    "failure_modes": ["crack", "capsule rupture"],
    "recovery_actions": ["liquid rupture", "gap bridging"],
    "key_constraints": [...]
  },
  "domain_analyses": {
    "materials_science": {
      "mechanical_properties": {...},
      "rupture_thresholds": {...},
      "failure_modes": [...],
      "risk_factors": [...]
    },
    "electrical_engineering": {
      "conductivity_restoration": {...},
      "resistance_changes": {...},
      "failure_modes": [...],
      "risk_factors": [...]
    }
  },
  "predicted_conflicts": [
    {
      "conflict_id": "CONF_001",
      "description": "Capsule size optimization conflict",
      "severity": 8,
      "domain_a": "Materials Science",
      "domain_b": "Electrical Engineering",
      "mechanism": "Smaller capsules rupture reliably BUT create narrow bridges with high resistance. Larger capsules provide good conductivity BUT fail to rupture.",
      "impact": "Cannot optimize for both rupture sensitivity AND conductivity; must choose trade-off.",
      "parameter_conflict": ["capsule_diameter_mm"]
    }
  ],
  "suggested_modifications": [
    {
      "modification_id": "MOD_001",
      "description": "Dual-size capsule system: 80% large (40mm) + 20% small (15mm)",
      "addresses_conflicts": ["CONF_001"],
      "implementation_notes": "Large capsules for conductivity, small for rupture sensitivity.",
      "feasibility": "medium",
      "trade_off_analysis": "Adds manufacturing complexity; resolves fundamental conflict."
    }
  ],
  "validation_status": "success",
  "error_log": []
}
```

## 🧠 Domain Heuristics (Encoded in Prompts)

### Materials Science
- Smaller capsules rupture at **lower stresses** (surface-area-to-volume ratio)
- Rupture stress depends **nonlinearly** (exponential) on capsule diameter
- Thermal cycling **degrades** capsule shells progressively (~30% per 100 cycles)
- Repeated healing cycles reduce polymer ductility
- Uniform distribution difficult for capsules < 20 μm

### Electrical Engineering
- Bridge resistance scales inversely with cross-section: $R = \rho \frac{L}{A}$
- Smaller bridges = **exponentially higher resistance**
- Liquid conductivity typically 100-1000 S/m
- RC time constant determines healing latency
- Evaporation degrades conductivity 30-50% per year
- Debris contamination increases resistance nonlinearly

### Conflict Detection Logic
- **Parameter conflicts**: Optimizing parameter X for Domain A requires opposing values in Domain B
- **Threshold conflicts**: Meeting Domain A's threshold violates Domain B's safe limits
- **Timescale conflicts**: Mismatched recovery timescales between domains
- **Material conflicts**: Material needs of Domain A violate constraints of Domain B

## 📝 Example: Self-Healing Conductor

### Input
```
A self-healing conductive material made from a polymer embedded with microcapsules 
containing a conductive liquid. When cracked, capsules rupture, liquid bridges the 
gap, restoring conductivity.
```

### Detected Conflicts (Example Output)

**CONF_001: Capsule Size Optimization Conflict**
- Severity: 8/10
- Mechanism: "Smaller capsules (10mm) rupture reliably at low stress BUT create narrow liquid bridges with resistance 50-100x higher. Larger capsules (50mm) have low-resistance bridges BUT fail to rupture under normal loads."
- Impact: Cannot simultaneously optimize for rupture sensitivity AND electrical conductivity

**CONF_002: Healing Timescale Conflict**
- Severity: 6/10
- Mechanism: "Materials science wants slow healing (thorough, less matrix stress). Electrical engineering needs FAST restoration (<10ms for some applications). Slow liquid bridge formation means high temporary resistance during healing window."

### Suggested Modifications (Example)

**MOD_001: Dual-Size Capsule System**
- Description: 80% large capsules (40mm) + 20% small capsules (15mm)
- Addresses: CONF_001
- Implementation: Large capsules ensure low-resistance bridges. Small capsules rupture first, triggering detection.
- Feasibility: Medium

**MOD_002: Hybrid Liquid Formula**
- Description: Conductive liquid + polymer nanofibers to reduce bridge resistance
- Addresses: CONF_001
- Implementation: Nanofibers reduce effective resistance 30-50% without larger capsules
- Feasibility: High

## 🔧 Configuration

### Environment Variables

```bash
# LLM Settings
export OPENROUTER_API_KEY="sk-or-your-key"
export LLM_TEMPERATURE="0.3"
export LLM_MAX_TOKENS="2000"

# Logging
export LOG_LEVEL="INFO"  # or DEBUG
```

### Model Selection

Recommended models for OpenRouter:

| Model | Speed | Cost | Reasoning | Use Case |
|-------|-------|------|-----------|----------|
| `gpt-3.5-turbo` | 2-5s | Low | Good | ✅ Default, recommended |
| `anthropic/claude-3-haiku` | 5-10s | Low | Excellent | ⭐ Better reasoning |
| `anthropic/claude-3-opus` | 10-15s | Medium | Excellent | ⭐⭐ Best reasoning |

To use a different model:
```bash
python -m src.main --design "..." --openrouter-model "anthropic/claude-3-haiku"
```

## 📁 Project Structure

```
design-validator/
├── src/
│   ├── agents/                    # Agent implementations
│   │   ├── parser_agent.py
│   │   ├── materials_agent.py
│   │   ├── electrical_agent.py
│   │   ├── conflict_agent.py
│   │   └── modification_agent.py
│   │
│   ├── graph/
│   │   ├── state.py              # TypedDict definitions
│   │   └── workflow.py           # LangGraph orchestration
│   │
│   ├── prompts/
│   │   ├── parser.py
│   │   ├── materials.py
│   │   ├── electrical.py
│   │   ├── conflict.py
│   │   └── modification.py
│   │
│   ├── schemas/
│   │   └── output_schemas.py     # Pydantic validators
│   │
│   ├── utils/
│   │   └── openrouter_client.py  # OpenRouter LLM client
│   │
│   └── main.py                   # CLI entry point
│
├── config/
│   └── settings.py               # Configuration
│
├── tests/
│   ├── test_agents.py
│   ├── test_workflow.py
│   └── test_integration.py
│
├── examples/
│   ├── sample_input.txt          # Example design
│   └── sample_output.json        # Example output
│
├── requirements.txt
├── README.md
└── docker-compose.yml            # Docker setup (optional)
```

## 🧪 Testing

```bash
# Run all tests
pytest tests/ -v

# Run with coverage
pytest tests/ --cov=src --cov-report=html

# Run specific test
pytest tests/test_workflow.py::test_full_workflow -v
```

## 🐳 Docker Deployment (Optional)

```bash
# Set OpenRouter API key
$env:OPENROUTER_API_KEY="sk-or-your-key"

# Start validator container
docker-compose up

# Or run directly
python -m src.main --design "Your design..." --output results/report.json
```

## 📚 Key Concepts

### Why LangGraph?
- **Explicit state management**: All agents operate on shared, typed state
- **Conditional routing**: Skip modification phase if no conflicts detected
- **Composability**: Easy to add more agents (mechanical, thermal, etc.)
- **Debuggability**: Clear execution trace of node transitions

### Why OpenRouter API?
- **Speed**: 2-5 second responses vs 30-120s for local LLMs
- **Flexibility**: 50+ models available (Claude, GPT-4, Mistral, etc.)
- **Low Cost**: Pay only for what you use (~$0.003-0.004 per design)
- **Reliability**: Redundant infrastructure, no local hardware required

### Why Few-Shot Prompting?
- No training data provided (constraint)
- First-principles reasoning encoded in system prompts
- Domain heuristics guide LLM reasoning
- Structured JSON output enforced

## ⚠️ Limitations & Future Work

### Current Limitations
- Limited to 2 domains (Materials + Electrical)
- LLM reasoning quality depends on model choice

### Future Enhancements
- Support 3+ domains (Thermal, Manufacturing, Cost)
- Iterative refinement: re-validate modifications
- Severity-based conflict prioritization
- Design modification validation loop
- Multi-turn clarification dialogues
- Caching for repeated design components
- Web UI for interactive design exploration

## 📖 References

### Prompt Engineering
- Few-shot examples for entity extraction
- Systematic conflict detection prompt (force parameter comparison)
- Trade-off analysis for modification synthesis

### Domain Knowledge
- Material science: fracture mechanics, healing mechanisms
- Electrical engineering: resistance, RC circuits, conductivity
- First-principles heuristics (e.g., R = ρL/A)

## 🤝 Contributing

1. Add new agents by implementing function with signature: `(state: DesignValidationState, llm: OpenRouterClient) -> DesignValidationState`
2. Register in `workflow.py` LangGraph
3. Add unit tests in `tests/`
4. Document domain heuristics in README

## 📄 License

This project is provided as-is for educational purposes.

## 👤 Author

Senior AI Engineer specializing in multi-agent systems and cross-domain design validation.

---

**Questions?** Check the `examples/` folder for sample workflows or review individual agent prompts in `src/prompts/`.

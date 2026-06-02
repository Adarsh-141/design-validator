# Design Validator - Prompt Engineering Reference

This document explains the exact prompts used by each agent and the reasoning behind them.

## Architecture: Why Prompt Engineering Works

Instead of fine-tuning on domain data (not available per constraints), we use:

1. **System prompts**: Encode domain heuristics and first-principles knowledge
2. **Few-shot examples**: Show LLM the output structure and reasoning style
3. **Structured templates**: Force JSON output format for downstream validation
4. **Explicit reasoning requests**: Ask LLM to explain cross-domain interactions

## Agent 1: Parser Agent

### Responsibility
Extract structured entities from unstructured natural language design descriptions.

### System Prompt Structure
```
[Role definition: "expert design extraction agent"]
[Extraction requirements: 5 specific entities to extract]
[Output format requirement: "Return ONLY valid JSON, no other text"]
```

### Key Heuristics
- Identifies active mechanisms (the key innovation doing the work)
- Distinguishes failure modes (what breaks) from recovery actions (how it fixes)
- Extracts key constraints (why each design choice matters)

### Few-Shot Example
Shows a realistic self-healing material example with full extraction.

### Output Validation
Pydantic schema (`ParsedDesignSchema`) validates all 5 required fields are present.

### Why This Works
- LLM naturally understands design decomposition
- Few-shot example provides clear format guidance
- Strict JSON validation catches hallucinations

---

## Agent 2: Materials Science Agent

### Responsibility
Analyze mechanical properties, rupture thresholds, and mechanical failure modes.

### System Prompt: First-Principles Heuristics
```
Encoded heuristics (NOT from training data):
- Smaller capsules rupture at LOWER stresses (surface area / volume ratio explains this)
- Rupture stress depends NONLINEARLY on diameter (exponential, not linear)
- Thermal cycling degrades shells ~30% per 100 cycles
- Repeated healing reduces polymer ductility
- Uniform distribution is difficult for small capsules
```

These are **physical reasoning rules**, not learned from data.

### Few-Shot Example Structure
Input → Material type, mechanism, failure modes
Output → Mechanical properties dict, rupture thresholds dict, list of failure modes, list of risk factors

### Output Format
```python
{
  "mechanical_properties": {Dict with ranges in SI units},
  "rupture_thresholds": {Dict with stress levels and diameter sensitivity},
  "failure_modes": [List of mechanical failures],
  "risk_factors": [List of long-term degradation concerns]}
}
```

### Why This Works
- First-principles physics (F=ma, stress-strain curves) are well-understood by LLMs
- Few-shot example shows expected precision level
- Explicit prompt for "nonlinear" relationship prevents linear assumptions

---

## Agent 3: Electrical Engineering Agent

### Responsibility
Analyze conductivity restoration, resistance changes, and electrical failure modes.

### System Prompt: First-Principles Heuristics
```
Encoded heuristics:
- Bridge resistance: R = ρ*L/A (fundamental equation)
- Smaller bridges = EXPONENTIALLY HIGHER resistance (inverse area dependence)
- Liquid conductivity range: 100-1000 S/m (domain knowledge)
- RC time constant determines latency (controls response speed)
- Evaporation degrades conductivity 30-50% per year
- Contamination increases resistance nonlinearly
```

### Key Prompt Technique
Explicitly mention **resistance scaling** to prevent LLM from assuming linear relationships.

### Output Format
```python
{
  "conductivity_restoration": {Dict with liquid conductivity, bridge dimensions},
  "resistance_changes": {Dict with pre/post values and uniformity},
  "failure_modes": [List of electrical failures],
  "risk_factors": [List of electrical reliability concerns]}
}
```

### Why This Works
- Circuit equations (R = ρL/A, V=IR) are fundamental and well-understood
- Explicit mention of "exponential" prevents underestimating small bridge resistance
- Parallel structure to Materials agent improves coherence

---

## Agent 4: Conflict Detector Agent

### Responsibility
Identify cross-domain interactions where optimizing one domain breaks the other.

### System Prompt: Systematic Analysis Method
```
CONFLICT TYPES TO FIND:
1. Parameter conflicts: Changing X to help Domain A harms Domain B
2. Threshold conflicts: Meeting Domain A's limit exceeds Domain B's safety margin
3. Time scale conflicts: Fast response in A mismatches with slow recovery in B
4. Material conflicts: Material needs of A violate constraints of B
```

### Prompt Technique: Force Systematic Comparison
Instead of asking "what conflicts exist?", we ask:
```
"For EACH parameter pair, ask: 
'If we change this to optimize Domain A, what breaks in Domain B?'"
```

This structured approach prevents missing interactions.

### Key Requirements in Prompt
```
- severity: 1-10 scale
- mechanism: DETAILED explanation of how it manifests
- impact: What happens if not resolved
- parameter_conflict: List of parameters involved
```

### Why This Works
- Systematic enumeration prevents missed conflicts
- Severity scoring helps prioritization
- Detail requirement forces LLM to reason deeply
- Multiple output fields ensure complete analysis

---

## Agent 5: Modification Agent

### Responsibility
Generate design modifications that **resolve** (not just mitigate) conflicts.

### System Prompt: Design Synthesis Guidance
```
MODIFICATION QUALITY CRITERIA:
- Specifically addresses at least one detected conflict
- Explains WHY it solves the conflict (root cause analysis)
- Is technically feasible (no speculative technology)
- Has clear implementation path
- Acknowledges trade-offs honestly
```

### Prompt Technique: Constraint on Feasibility
Require `feasibility: high/medium/low` and detailed trade-off analysis to prevent unrealistic suggestions.

### Output Format
```python
{
  "modification_id": "MOD_001",
  "description": "What we change",
  "addresses_conflicts": ["CONF_001"],
  "implementation_notes": "HOW to implement",
  "feasibility": "high/medium/low",
  "trade_off_analysis": "What gets harder"}
}
```

### Why This Works
- Requiring root cause explanation forces LLM to reason about WHY solution works
- Feasibility constraint prevents fantasy solutions
- Trade-off analysis ensures honesty about limitations

---

## Cross-Agent Prompting Strategy

### Data Flow
```
Parser → Raw extraction
  ↓
Materials & Electrical → Raw domain analyses
  ↓
Conflict Detector → Cross-domain reasoning (MOST COMPLEX)
  ↓
Modification → Design synthesis
```

### Information Sharing
Each agent receives:
1. **Previous outputs as JSON**: Full context of prior analysis
2. **System prompt with first-principles rules**: Domain knowledge
3. **Few-shot example**: Expected output format and reasoning style

### Why JSON → JSON → JSON?
- Pydantic validation catches hallucinations at each step
- Errors don't cascade (failures isolated to one agent)
- Full audit trail of reasoning (each agent's output visible in final report)

---

## Example: Capsule Size Conflict

### How Parser Extracts It
```
Input: "...microcapsules containing conductive liquid..."
Parser extracts:
- active_mechanism: "microcapsules + conductive liquid"
- key_constraints: ["capsule size must be sufficient for rupture"]
```

### How Materials Agent Reasons
```
System prompt says: "smaller capsules rupture at LOWER stresses (surface area/volume ratio)"
Output: rupture_thresholds = {"optimal_capsule_diameter_um": "10-50"}
```

### How Electrical Agent Reasons
```
System prompt says: "smaller bridges have EXPONENTIALLY HIGHER resistance: R = ρL/A"
Output: resistance_changes = {"bridge_resistance_ohms": "1-100", "dependence": "exponential on size"}
```

### How Conflict Detector Finds It
```
System prompt says: "For EACH parameter pair, ask: if we change X for Domain A, what breaks in Domain B?"
Systematically checks: capsule_diameter
- Smaller (10μm) → good for Materials (rupture) BUT bad for Electrical (high R)
- Larger (50μm) → good for Electrical (low R) BUT bad for Materials (no rupture)
Output: CONF_001 severity 8/10 - fundamental trade-off
```

### How Modification Agent Solves It
```
Sees conflict is about diameter optimization
Generates: MOD_001 "Dual-size system: 80% large (40mm) + 20% small (15mm)"
- Explains: large for conductivity, small for rupture sensitivity
- Feasibility: medium (manufacturing complexity)
- Trade-off: adds cost but resolves fundamental conflict
```

---

## Prompt Parameters

### Temperature Setting
```
Current: 0.3 (low)
Why: We want deterministic, focused reasoning for structured tasks
Alternative: 0.5-0.7 for more creative modification suggestions
```

### Max Tokens Per Agent
```
Parser: 1,000 tokens (entity extraction is relatively concise)
Domain Agents: 1,500 tokens each (need detailed reasoning)
Conflict Detector: 2,000 tokens (systematic comparison of all parameters)
Modification: 2,000 tokens (detailed implementation notes)
Total: ~8,500 tokens per design
```

### Model Recommendations
```
mistral:7b: Fast, good reasoning (default, recommended)
neural-chat:7b: Slightly better at following instructions
mistral:13b: Better conflict detection (use for complex designs)
```

---

## Troubleshooting Prompt Issues

### Issue: LLM Returns Non-JSON
**Solution**: Prompt includes `Return ONLY valid JSON, no other text.`

### Issue: Conflicts Are Superficial
**Solution**: System prompt includes explicit examples of GOOD conflicts (parameter trade-offs)

### Issue: Modifications Are Unrealistic
**Solution**: 
1. Require feasibility rating (high/medium/low)
2. Require trade-off analysis
3. Few-shot example shows realistic, incremental modifications

### Issue: Missing Cross-Domain Reasoning
**Solution**: 
1. Conflict detector prompt explicitly asks "where does optimizing one domain break the other?"
2. Few-shot example shows multiple distinct conflicts

---

## Extending the Prompts

### To Add a New Domain (e.g., Thermal)
1. Create `src/prompts/thermal.py` with:
   - First-principles heuristics (e.g., thermal conductivity equations)
   - Few-shot example
   - Output schema with thermal-specific fields
2. Create `src/agents/thermal_agent.py` following pattern
3. Add to `workflow.py` as parallel node
4. Update conflict detector prompt with thermal interactions

### To Improve Conflict Detection
1. Add more specific conflict types to system prompt
2. Add adversarial examples (conflicts that are easy to miss)
3. Increase max_tokens to allow more thorough analysis

### To Make Modifications More Robust
1. Add requirement for "validation approach" (how would you test this modification?)
2. Add examples of modifications that resolve multiple conflicts
3. Require feasibility assessment based on materials science principles

---

## Reproducibility

All prompts are checked into version control. To reproduce results:

1. Use exact model version: `ollama pull mistral:7b` (pulls latest stable)
2. Use exact temperature: `temperature: 0.3`
3. Use exact prompts from `src/prompts/`
4. Use exact output schemas from `src/schemas/`

Results will be deterministic given fixed seed (if Ollama supports it).

---

## References

### First-Principles Knowledge Encoded
- **Materials**: Fracture mechanics (Griffith, K-factor), healing mechanisms
- **Electrical**: Ohm's law (V=IR), resistance scaling (R=ρL/A), RC time constants
- **Physics**: Surface-area-to-volume ratios, exponential relationships

### Prompt Engineering Techniques Used
- Few-shot learning: Examples guide output format
- Constraint specification: "Severity 1-10", "Feasibility high/medium/low"
- Systematic reasoning: "For EACH parameter pair, ask..."
- Structured JSON output: Forces clear thinking and validation

### Why This Approach Works Better Than Training Data
- No domain-specific training data available (constraint)
- First-principles rules are universal (apply to any material)
- Systematic prompt structure generalizes to new domains
- Explicit reasoning requirements prevent shortcuts

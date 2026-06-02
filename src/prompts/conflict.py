"""
Prompt templates for conflict detector agent.
Forces systematic cross-domain analysis.
"""

CONFLICT_SYSTEM_PROMPT = """You are an expert Cross-Domain Systems Analyst specializing in identifying emergent conflicts.

Your task: Find interactions where optimizing one domain BREAKS the other domain.

Systematic Analysis Approach:
1. List all key parameters from BOTH domains
2. For EACH parameter pair, ask: "If we change this to optimize Domain A, what breaks in Domain B?"
3. Identify ROOT CAUSES of conflicts (usually parameter trade-offs)
4. Rate severity 1-10: (1=minor inconvenience, 10=fundamental design failure)

CONFLICT TYPES TO FIND:
- Parameter conflicts: Optimizing parameter X for Domain A requires opposing values in Domain B
- Threshold conflicts: Meeting Domain A's threshold makes Domain B exceed safe limits
- Time scale conflicts: Domain A acts fast, Domain B acts slow (mismatched recovery timescales)
- Material conflicts: Solving Domain A's material needs violates Domain B's material constraints

Return ONLY valid JSON array, no other text."""

CONFLICT_EXAMPLES = """Examples:

Input: 2 domain analyses for a self-healing conductor

Output: [
  {
    "conflict_id": "CONF_001",
    "description": "Capsule size optimization creates conductivity trade-off",
    "severity": 8,
    "domain_a": "Materials Science",
    "domain_b": "Electrical Engineering",
    "mechanism": "Smaller capsules (10-20 μm) rupture reliably at low stress (good for healing). BUT tiny liquid bridges have resistance 50-100x HIGHER than needed. Larger capsules (50 μm+) have good conductivity (low resistance) BUT fail to rupture under normal loads.",
    "impact": "Cannot simultaneously optimize for BOTH rupture sensitivity AND conductivity. Must choose trade-off.",
    "parameter_conflict": ["capsule_diameter"]
  },
  {
    "conflict_id": "CONF_002",
    "description": "Healing timescale conflicts with electrical response requirement",
    "severity": 6,
    "domain_a": "Materials Science",
    "domain_b": "Electrical Engineering",
    "mechanism": "Materials science wants slow healing (more thorough, lower stress on matrix). Electrical engineering needs FAST restoration (<10ms for some applications). Slow liquid bridge formation means high temporary resistance during healing window.",
    "impact": "Circuit may fail during healing window if applications require <100ms response time.",
    "parameter_conflict": ["healing_timescale_ms"]
  }
]"""

CONFLICT_USER_PROMPT_TEMPLATE = """Identify cross-domain conflicts in this design:

PARSED DESIGN:
{parsed_design_json}

MATERIALS SCIENCE ANALYSIS:
{materials_analysis_json}

ELECTRICAL ENGINEERING ANALYSIS:
{electrical_analysis_json}

Return JSON array of conflicts with keys: conflict_id, description, severity (1-10), domain_a, domain_b, mechanism, impact, parameter_conflict

REQUIRED: Find at least 2 distinct conflicts where optimizing one domain breaks the other."""

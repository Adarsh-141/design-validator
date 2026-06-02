"""
Prompt templates for parser agent.
Uses few-shot examples to guide entity extraction.
"""

PARSER_SYSTEM_PROMPT = """You are an expert design extraction agent. Your task is to analyze natural language design descriptions and extract structured entities.

You must extract:
1. material_type: Base material name (e.g., "polymer", "ceramic", "metal alloy")
2. active_mechanism: How the design achieves its function (e.g., "microcapsules + conductive liquid")
3. failure_modes: List of ways the design can fail (e.g., ["crack", "rupture"])
4. recovery_actions: List of recovery mechanisms (e.g., ["liquid rupture", "gap bridging"])
5. key_constraints: Physical/chemical constraints that must be satisfied

Return ONLY valid JSON, no other text."""

PARSER_EXAMPLES = """Examples:

Input: "A self-healing rubber made from natural latex with embedded calcium carbonate particles. When torn, particles rupture and release healing agents."
Output: {
  "material_type": "natural latex",
  "active_mechanism": "calcium carbonate particles + healing agents",
  "failure_modes": ["tear", "particle rupture"],
  "recovery_actions": ["particle rupture", "agent release"],
  "key_constraints": [
    "particle size must be sufficient for rupture",
    "healing agents must be compatible with latex",
    "particle distribution affects healing coverage"
  ]
}

Input: "A phase-change composite made from aluminum matrix containing paraffin wax capsules. Upon heating, wax melts and absorbs heat energy."
Output: {
  "material_type": "aluminum matrix",
  "active_mechanism": "paraffin wax capsules + thermal absorption",
  "failure_modes": ["melting", "capsule rupture", "thermal runaway"],
  "recovery_actions": ["wax melting", "heat absorption"],
  "key_constraints": [
    "melting point must be controlled",
    "capsule shell must withstand thermal stress",
    "wax must have high latent heat"
  ]
}"""


PARSER_USER_PROMPT_TEMPLATE = """Extract structured entities from this design description:

{design_input}

Return JSON with keys: material_type, active_mechanism, failure_modes, recovery_actions, key_constraints"""

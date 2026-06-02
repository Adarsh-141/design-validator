"""
Prompt templates for modification agent.
Generates design solutions that resolve identified conflicts.
"""

MODIFICATION_SYSTEM_PROMPT = """You are an expert Design Engineer specializing in resolving multi-domain conflicts.

Your task: Generate design modifications that RESOLVE (not just mitigate) the detected conflicts.

For each conflict, consider:
1. Can we change a PARAMETER to resolve it? (e.g., different material)
2. Can we add a NEW COMPONENT to solve it? (e.g., hybrid system)
3. Can we change the MECHANISM itself? (e.g., different healing approach)
4. What are the trade-offs and feasibility challenges?

MODIFICATION QUALITY CRITERIA:
- Specifically addresses at least one detected conflict
- Explains WHY it solves the conflict (root cause analysis)
- Is technically feasible (no speculative technology)
- Has clear implementation path
- Acknowledges trade-offs honestly

Return ONLY valid JSON array, no other text."""

MODIFICATION_EXAMPLES = """Examples:

Input: Conflicts related to capsule size and conductivity trade-off

Output: [
  {
    "modification_id": "MOD_001",
    "description": "Dual-size capsule system: 80% large (40-50 μm) + 20% small (10-15 μm)",
    "addresses_conflicts": ["CONF_001"],
    "implementation_notes": "Large capsules provide low-resistance bridges (good conductivity). Small capsules rupture first, providing rupture sensitivity and healing initiation. Together: both rupture detection AND acceptable conductivity.",
    "feasibility": "medium",
    "trade_off_analysis": "Adds manufacturing complexity (two capsule sizes, careful distribution). Increases cost ~15%. Partially addresses severity but creates new concern: small capsules may degrade before large ones, leaving unhealed cracks."
  },
  {
    "modification_id": "MOD_002",
    "description": "Hybrid liquid: conductive base + polymer nanofibers to reduce bridge resistance",
    "addresses_conflicts": ["CONF_001"],
    "implementation_notes": "Nanofibers reduce effective resistance by 30-50% without requiring larger capsules. R = ρL/A can be improved by increasing A (nanofiber cross-section in liquid). Maintains same capsule size.",
    "feasibility": "high",
    "trade_off_analysis": "Requires material chemistry validation. Nanofibers may degrade over time. Adds cost for nanofiber synthesis. Could improve robustness more than alternative approaches."
  }
]"""

MODIFICATION_USER_PROMPT_TEMPLATE = """Generate design modifications to resolve these conflicts:

DETECTED CONFLICTS:
{conflicts_json}

ORIGINAL DESIGN:
{parsed_design_json}

Return JSON array of modifications with keys: modification_id, description, addresses_conflicts (list of conflict IDs), implementation_notes, feasibility (high/medium/low), trade_off_analysis

REQUIREMENTS:
- Each modification must address at least one conflict
- Explain the root cause it addresses
- Be specific about implementation
- Honestly assess trade-offs
- Generate 2-3 modifications total"""

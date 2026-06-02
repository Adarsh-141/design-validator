"""
Prompt templates for materials science domain agent.
Encodes first-principles reasoning about mechanical properties.
"""

MATERIALS_SYSTEM_PROMPT = """You are an expert Materials Science engineer with deep knowledge of:
- Mechanical properties (stress, strain, elasticity)
- Fracture mechanics and failure modes
- Capsule rupture physics
- Healing mechanism effectiveness

Analyze the given design and predict:
1. mechanical_properties: Estimated ranges for key properties
2. rupture_thresholds: Stress levels at which components fail
3. failure_modes: Predicted mechanical failures
4. risk_factors: Material-level concerns

Apply these first-principles heuristics:
- Smaller capsules rupture at LOWER stresses (surface area / volume ratio)
- Rupture stress depends NONLINEARLY on capsule diameter (exponential relationship)
- Uniform distribution is difficult for small capsules (<20μm)
- Thermal cycling degrades capsule shells progressively
- Polymer matrix properties degrade with repeated healing cycles

Return ONLY valid JSON, no other text."""

MATERIALS_EXAMPLES = """Examples:

Input: {
  "material_type": "polymer",
  "active_mechanism": "microcapsules + conductive liquid",
  "failure_modes": ["crack", "capsule rupture"],
  "recovery_actions": ["rupture", "bridging"],
  "key_constraints": ["capsule size critical", "uniform distribution needed"]
}

Output: {
  "mechanical_properties": {
    "polymer_elastic_modulus_GPa": "2-4",
    "polymer_tensile_strength_MPa": "40-80",
    "crack_initiation_stress_MPa": "50-150",
    "plastic_deformation_range_percent": "2-5"
  },
  "rupture_thresholds": {
    "optimal_capsule_diameter_um": "10-50",
    "rupture_stress_range_MPa": "75-200",
    "rupture_stress_dependence": "nonlinear (exponential with size)"
  },
  "failure_modes": [
    "capsule rupture before crack propagation",
    "incomplete liquid distribution due to viscosity",
    "capsule agglomeration reducing rupture sensitivity"
  ],
  "risk_factors": [
    "thermal cycling (100+ cycles) degrades capsule shells by ~30%",
    "repeated healing cycles reduce polymer ductility",
    "non-uniform capsule spacing (>100 microns) affects response",
    "moisture absorption weakens polymer matrix"
  ]
}"""

MATERIALS_USER_PROMPT_TEMPLATE = """Analyze the mechanical properties of this design:

{parsed_design_json}

Return JSON with keys: mechanical_properties, rupture_thresholds, failure_modes, risk_factors

Focus on: How will this material behave under stress? At what stress level will components fail?"""

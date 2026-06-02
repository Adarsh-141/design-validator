"""
Materials Science Domain Agent - Analyzes mechanical properties and failure modes.
"""

import json
import logging
from typing import Optional
from src.graph.state import DesignValidationState, MechanicalAnalysis
from src.utils.llm_client import OllamaClient
from src.prompts.materials import (
    MATERIALS_SYSTEM_PROMPT,
    MATERIALS_EXAMPLES,
    MATERIALS_USER_PROMPT_TEMPLATE
)
from src.schemas.output_schemas import MaterialsAnalysisSchema

logger = logging.getLogger(__name__)


def analyze_materials(state: DesignValidationState, llm: OllamaClient) -> DesignValidationState:
    """
    Analyze materials science domain: mechanical properties, rupture thresholds, failure modes.
    
    Input State: parsed_design (ParsedDesignEntity)
    Output State: materials_analysis
    """
    parsed_design = state.get("parsed_design")
    
    if not parsed_design:
        error_msg = "No parsed design available"
        if "domain_analysis_errors" not in state:
            state["domain_analysis_errors"] = []
        state["domain_analysis_errors"].append(error_msg)
        logger.warning(error_msg)
        return state
    
    try:
        # Construct prompt
        system_prompt = MATERIALS_SYSTEM_PROMPT + "\n\n" + MATERIALS_EXAMPLES
        parsed_design_json = json.dumps(parsed_design, indent=2)
        user_prompt = MATERIALS_USER_PROMPT_TEMPLATE.format(
            parsed_design_json=parsed_design_json
        )
        
        logger.info("Analyzing materials science domain...")
        
        # Generate and parse JSON
        response_json = llm.generate_json(
            prompt=user_prompt,
            system_prompt=system_prompt,
            max_tokens=1000
        )
        
        # Validate with Pydantic schema
        analysis = MaterialsAnalysisSchema(**response_json)
        
        # Convert to TypedDict
        state["materials_analysis"] = MechanicalAnalysis(
            mechanical_properties=analysis.mechanical_properties,
            rupture_thresholds=analysis.rupture_thresholds,
            failure_modes=analysis.failure_modes,
            risk_factors=analysis.risk_factors
        )
        
        logger.info(f"✓ Materials analysis complete")
        logger.info(f"  Failure modes: {len(analysis.failure_modes)}")
        logger.info(f"  Risk factors: {len(analysis.risk_factors)}")
        
        return state
        
    except json.JSONDecodeError as e:
        error_msg = f"Materials agent: Invalid JSON: {str(e)}"
        if "domain_analysis_errors" not in state:
            state["domain_analysis_errors"] = []
        state["domain_analysis_errors"].append(error_msg)
        logger.error(error_msg)
        return state
    except Exception as e:
        error_msg = f"Materials analysis failed: {str(e)}"
        if "domain_analysis_errors" not in state:
            state["domain_analysis_errors"] = []
        state["domain_analysis_errors"].append(error_msg)
        logger.error(error_msg)
        return state

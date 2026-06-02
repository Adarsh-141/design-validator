"""
Electrical Engineering Domain Agent - Analyzes conductivity and electrical properties.
"""

import json
import logging
from typing import Optional
from src.graph.state import DesignValidationState, ElectricalAnalysis
from src.utils.llm_client import OllamaClient
from src.prompts.electrical import (
    ELECTRICAL_SYSTEM_PROMPT,
    ELECTRICAL_EXAMPLES,
    ELECTRICAL_USER_PROMPT_TEMPLATE
)
from src.schemas.output_schemas import ElectricalAnalysisSchema

logger = logging.getLogger(__name__)


def analyze_electrical(state: DesignValidationState, llm: OllamaClient) -> DesignValidationState:
    """
    Analyze electrical engineering domain: conductivity, resistance, electrical failure modes.
    
    Input State: parsed_design (ParsedDesignEntity)
    Output State: electrical_analysis
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
        system_prompt = ELECTRICAL_SYSTEM_PROMPT + "\n\n" + ELECTRICAL_EXAMPLES
        parsed_design_json = json.dumps(parsed_design, indent=2)
        user_prompt = ELECTRICAL_USER_PROMPT_TEMPLATE.format(
            parsed_design_json=parsed_design_json
        )
        
        logger.info("Analyzing electrical engineering domain...")
        
        # Generate and parse JSON
        response_json = llm.generate_json(
            prompt=user_prompt,
            system_prompt=system_prompt,
            max_tokens=1000
        )
        
        # Validate with Pydantic schema
        analysis = ElectricalAnalysisSchema(**response_json)
        
        # Convert to TypedDict
        state["electrical_analysis"] = ElectricalAnalysis(
            conductivity_restoration=analysis.conductivity_restoration,
            resistance_changes=analysis.resistance_changes,
            failure_modes=analysis.failure_modes,
            risk_factors=analysis.risk_factors
        )
        
        logger.info(f"✓ Electrical analysis complete")
        logger.info(f"  Failure modes: {len(analysis.failure_modes)}")
        logger.info(f"  Risk factors: {len(analysis.risk_factors)}")
        
        return state
        
    except json.JSONDecodeError as e:
        error_msg = f"Electrical agent: Invalid JSON: {str(e)}"
        if "domain_analysis_errors" not in state:
            state["domain_analysis_errors"] = []
        state["domain_analysis_errors"].append(error_msg)
        logger.error(error_msg)
        return state
    except Exception as e:
        error_msg = f"Electrical analysis failed: {str(e)}"
        if "domain_analysis_errors" not in state:
            state["domain_analysis_errors"] = []
        state["domain_analysis_errors"].append(error_msg)
        logger.error(error_msg)
        return state

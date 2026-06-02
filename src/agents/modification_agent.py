"""
Modification Agent - Generates design modifications to resolve detected conflicts.
"""

import json
import logging
from typing import List, Optional
from src.graph.state import DesignValidationState, DesignModification
from src.utils.llm_client import OllamaClient
from src.prompts.modification import (
    MODIFICATION_SYSTEM_PROMPT,
    MODIFICATION_EXAMPLES,
    MODIFICATION_USER_PROMPT_TEMPLATE
)
from src.schemas.output_schemas import ModificationSchema

logger = logging.getLogger(__name__)


def suggest_modifications(state: DesignValidationState, llm: OllamaClient) -> DesignValidationState:
    """
    Generate design modifications that resolve detected conflicts.
    
    Input State: parsed_design, detected_conflicts
    Output State: suggested_modifications
    """
    parsed_design = state.get("parsed_design")
    detected_conflicts = state.get("detected_conflicts", [])
    
    # Check prerequisites
    if not parsed_design:
        logger.warning("Cannot suggest modifications: no parsed design")
        state["suggested_modifications"] = []
        return state
    
    if not detected_conflicts:
        logger.info("No conflicts to resolve; skipping modifications")
        state["suggested_modifications"] = []
        return state
    
    try:
        # Construct prompt
        system_prompt = MODIFICATION_SYSTEM_PROMPT + "\n\n" + MODIFICATION_EXAMPLES
        
        parsed_json = json.dumps(parsed_design, indent=2)
        conflicts_json = json.dumps(detected_conflicts, indent=2)
        
        user_prompt = MODIFICATION_USER_PROMPT_TEMPLATE.format(
            parsed_design_json=parsed_json,
            conflicts_json=conflicts_json
        )
        
        logger.info(f"Generating design modifications for {len(detected_conflicts)} conflicts...")
        
        # Generate and parse JSON
        response_json = llm.generate_json(
            prompt=user_prompt,
            system_prompt=system_prompt,
            max_tokens=1500
        )
        
        # Handle both formats: {"modifications": [...]} or direct array [...]
        if isinstance(response_json, dict):
            modifications_list = response_json.get("modifications", [])
        else:
            modifications_list = response_json
        
        if not isinstance(modifications_list, list):
            logger.warning(f"Expected list of modifications, got {type(modifications_list)}")
            modifications_list = []
        
        # Validate each modification with Pydantic
        validated_modifications: List[DesignModification] = []
        for mod in modifications_list:
            try:
                validated = ModificationSchema(**mod)
                validated_modifications.append(DesignModification(
                    modification_id=validated.modification_id,
                    description=validated.description,
                    addresses_conflicts=validated.addresses_conflicts,
                    implementation_notes=validated.implementation_notes,
                    feasibility=validated.feasibility,
                    trade_off_analysis=validated.trade_off_analysis
                ))
            except Exception as e:
                logger.warning(f"Skipping invalid modification: {str(e)}")
                continue
        
        state["suggested_modifications"] = validated_modifications
        
        logger.info(f"✓ Modification suggestion complete")
        logger.info(f"  Modifications suggested: {len(validated_modifications)}")
        for mod in validated_modifications:
            logger.info(f"    - {mod['modification_id']}: {mod['feasibility']} feasibility")
        
        return state
        
    except json.JSONDecodeError as e:
        error_msg = f"Modification agent: Invalid JSON: {str(e)}"
        logger.error(error_msg)
        state["suggested_modifications"] = []
        return state
    except Exception as e:
        error_msg = f"Modification suggestion failed: {str(e)}"
        logger.error(error_msg)
        state["suggested_modifications"] = []
        return state

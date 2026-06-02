"""
Conflict Detector Agent - Identifies cross-domain emergent conflicts.
"""

import json
import logging
from typing import List, Optional
from src.graph.state import DesignValidationState, DomainConflict
from src.utils.llm_client import OllamaClient
from src.prompts.conflict import (
    CONFLICT_SYSTEM_PROMPT,
    CONFLICT_EXAMPLES,
    CONFLICT_USER_PROMPT_TEMPLATE
)
from src.schemas.output_schemas import ConflictSchema

logger = logging.getLogger(__name__)


def detect_conflicts(state: DesignValidationState, llm: OllamaClient) -> DesignValidationState:
    """
    Detect cross-domain conflicts where optimizing one domain breaks the other.
    
    Input State: parsed_design, materials_analysis, electrical_analysis
    Output State: detected_conflicts
    """
    parsed_design = state.get("parsed_design")
    materials_analysis = state.get("materials_analysis")
    electrical_analysis = state.get("electrical_analysis")
    
    # Check prerequisites
    if not parsed_design:
        logger.warning("Cannot detect conflicts: no parsed design")
        state["detected_conflicts"] = []
        return state
    
    if not materials_analysis or not electrical_analysis:
        logger.warning("Cannot detect conflicts: missing domain analyses")
        state["detected_conflicts"] = []
        return state
    
    try:
        # Construct prompt
        system_prompt = CONFLICT_SYSTEM_PROMPT + "\n\n" + CONFLICT_EXAMPLES
        
        parsed_json = json.dumps(parsed_design, indent=2)
        materials_json = json.dumps(materials_analysis, indent=2)
        electrical_json = json.dumps(electrical_analysis, indent=2)
        
        user_prompt = CONFLICT_USER_PROMPT_TEMPLATE.format(
            parsed_design_json=parsed_json,
            materials_analysis_json=materials_json,
            electrical_analysis_json=electrical_json
        )
        
        logger.info("Detecting cross-domain conflicts...")
        
        # Generate and parse JSON
        response_json = llm.generate_json(
            prompt=user_prompt,
            system_prompt=system_prompt,
            max_tokens=1500
        )
        
        # Handle both formats: {"conflicts": [...]} or direct array [...]
        if isinstance(response_json, dict):
            conflicts_list = response_json.get("conflicts", [])
        else:
            conflicts_list = response_json
        
        if not isinstance(conflicts_list, list):
            logger.warning(f"Expected list of conflicts, got {type(conflicts_list)}")
            conflicts_list = []
        
        # Validate each conflict with Pydantic
        validated_conflicts: List[DomainConflict] = []
        for conf in conflicts_list:
            try:
                validated = ConflictSchema(**conf)
                validated_conflicts.append(DomainConflict(
                    conflict_id=validated.conflict_id,
                    description=validated.description,
                    severity=validated.severity,
                    domain_a=validated.domain_a,
                    domain_b=validated.domain_b,
                    mechanism=validated.mechanism,
                    impact=validated.impact,
                    parameter_conflict=validated.parameter_conflict
                ))
            except Exception as e:
                logger.warning(f"Skipping invalid conflict: {str(e)}")
                continue
        
        state["detected_conflicts"] = validated_conflicts
        
        logger.info(f"✓ Conflict detection complete")
        logger.info(f"  Conflicts found: {len(validated_conflicts)}")
        for conf in validated_conflicts:
            logger.info(f"    - {conf['conflict_id']}: severity {conf['severity']}/10")
        
        return state
        
    except json.JSONDecodeError as e:
        error_msg = f"Conflict detector: Invalid JSON: {str(e)}"
        logger.error(error_msg)
        state["detected_conflicts"] = []
        return state
    except Exception as e:
        error_msg = f"Conflict detection failed: {str(e)}"
        logger.error(error_msg)
        state["detected_conflicts"] = []
        return state

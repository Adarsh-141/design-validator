"""
Parser Agent - Extracts structured entities from natural language design descriptions.
"""

import json
import logging
from typing import Optional
from src.graph.state import DesignValidationState, ParsedDesignEntity
from src.utils.llm_client import OllamaClient
from src.prompts.parser import (
    PARSER_SYSTEM_PROMPT,
    PARSER_EXAMPLES,
    PARSER_USER_PROMPT_TEMPLATE
)
from src.schemas.output_schemas import ParsedDesignSchema

logger = logging.getLogger(__name__)


def parse_design(state: DesignValidationState, llm: OllamaClient) -> DesignValidationState:
    """
    Parse natural language design description into structured entities.
    
    Input State: design_input (str)
    Output State: parsed_design, parse_error
    """
    design_input = state.get("design_input", "")
    
    if not design_input or not design_input.strip():
        state["parse_error"] = "Empty design input"
        logger.error("Parse failed: empty input")
        return state
    
    try:
        # Construct prompt with examples
        system_prompt = PARSER_SYSTEM_PROMPT + "\n\n" + PARSER_EXAMPLES
        user_prompt = PARSER_USER_PROMPT_TEMPLATE.format(design_input=design_input)
        
        logger.info(f"Parsing design (length: {len(design_input)} chars)...")
        
        # Generate and parse JSON
        response_json = llm.generate_json(
            prompt=user_prompt,
            system_prompt=system_prompt,
            max_tokens=500
        )
        
        # Validate with Pydantic schema
        parsed = ParsedDesignSchema(**response_json)
        
        # Convert to TypedDict
        state["parsed_design"] = ParsedDesignEntity(
            material_type=parsed.material_type,
            active_mechanism=parsed.active_mechanism,
            failure_modes=parsed.failure_modes,
            recovery_actions=parsed.recovery_actions,
            key_constraints=parsed.key_constraints
        )
        state["parse_error"] = None
        
        logger.info(f"✓ Parse successful: {parsed.material_type}")
        logger.info(f"  Mechanism: {parsed.active_mechanism}")
        logger.info(f"  Failure modes: {len(parsed.failure_modes)}")
        
        return state
        
    except json.JSONDecodeError as e:
        error_msg = f"Invalid JSON from parser: {str(e)}"
        state["parse_error"] = error_msg
        logger.error(error_msg)
        return state
    except Exception as e:
        error_msg = f"Parse failed: {str(e)}"
        state["parse_error"] = error_msg
        logger.error(error_msg)
        return state

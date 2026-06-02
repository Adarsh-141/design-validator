"""
Main entry point for the design validator system.
OpenRouter backend for fast LLM inference.
"""

import json
import logging
import sys
import os
from pathlib import Path
from typing import Optional
from src.graph.state import DesignValidationState
from src.graph.workflow import DesignValidatorGraph
from src.utils.openrouter_client import OpenRouterClient
from config.settings import OPENROUTER_API_KEY, OPENROUTER_MODEL

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def setup_logging(verbose: bool = False) -> None:
    """Configure logging verbosity."""
    level = logging.DEBUG if verbose else logging.INFO
    for handler in logging.root.handlers:
        handler.setLevel(level)
    logging.getLogger(__name__).setLevel(level)


def validate_design(
    design_input: str,
    openrouter_api_key: Optional[str] = None,
    openrouter_model: Optional[str] = None,
    output_file: Optional[str] = None,
    verbose: bool = False
) -> dict:
    """
    Validate a design description for cross-domain conflicts.
    
    Args:
        design_input: Natural language design description
        openrouter_api_key: OpenRouter API key (defaults to .env)
        openrouter_model: Model name for OpenRouter (defaults to .env)
        output_file: Optional path to save JSON report
        verbose: Enable debug logging
        
    Returns:
        Validation report dictionary
    """
    setup_logging(verbose)
    
    try:
        # Use provided values or fall back to .env configuration
        api_key = openrouter_api_key or OPENROUTER_API_KEY
        model = openrouter_model or OPENROUTER_MODEL
        
        logger.info(f"Using OpenRouter backend with model: {model}")
        llm = OpenRouterClient(
            api_key=api_key,
            model=model,
            temperature=0.3
        )
        
        # Create and execute workflow
        graph = DesignValidatorGraph(llm)
        
        initial_state: DesignValidationState = {
            "design_input": design_input
        }
        
        final_state = graph.invoke(initial_state)
        report = final_state.get("validation_report", {})
        
        # Save output if requested
        if output_file:
            output_path = Path(output_file)
            output_path.parent.mkdir(parents=True, exist_ok=True)
            with open(output_path, 'w') as f:
                json.dump(report, f, indent=2)
            logger.info(f"Report saved to {output_path}")
        
        return report
        
    except Exception as e:
        logger.error(f"Validation failed: {str(e)}", exc_info=True)
        return {
            "validation_status": "failed",
            "error": str(e)
        }


def main():
    """CLI entry point."""
    import argparse
    
    parser = argparse.ArgumentParser(
        description="Design Validator - Multi-Agent Cross-Domain Analysis",
        epilog="Examples:\n"
               "  python -m src.main --design \"Your design...\"\n"
               "  python -m src.main --design \"...\" -o report.json\n"
               "  python -m src.main --design \"...\" -m anthropic/claude-3-haiku",
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    parser.add_argument(
        "--design", "-d",
        required=True,
        help="Design description (natural language)"
    )
    parser.add_argument(
        "--output", "-o",
        default="results/report.json",
        help="Output JSON file path (default: results/report.json)"
    )
    parser.add_argument(
        "--model", "-m",
        help="OpenRouter model (uses .env default if not specified)"
    )
    parser.add_argument(
        "--key", "-k",
        help="OpenRouter API key (uses .env default if not specified)"
    )
    parser.add_argument(
        "--verbose", "-v",
        action="store_true",
        help="Enable debug logging"
    )
    
    args = parser.parse_args()
    
    report = validate_design(
        design_input=args.design,
        openrouter_api_key=args.key,
        openrouter_model=args.model,
        output_file=args.output,
        verbose=args.verbose
    )
    
    # Print summary
    print("\n" + "=" * 60)
    print("VALIDATION REPORT SUMMARY")
    print("=" * 60)
    print(f"Status: {report.get('validation_status', 'unknown')}")
    
    conflicts = report.get('predicted_conflicts', [])
    print(f"Conflicts Found: {len(conflicts)}")
    for conf in conflicts:
        print(f"  - {conf['conflict_id']} (severity {conf['severity']}/10): {conf['description'][:60]}...")
    
    mods = report.get('suggested_modifications', [])
    print(f"Modifications Suggested: {len(mods)}")
    for mod in mods:
        print(f"  - {mod['modification_id']}: {mod['description'][:60]}...")
    
    print("=" * 60)
    print(f"\nFull report saved to: {args.output}")
    
    return 0


if __name__ == "__main__":
    sys.exit(main())

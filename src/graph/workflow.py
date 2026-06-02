"""
LangGraph workflow construction and orchestration.
"""

import logging
import time
from datetime import datetime
from typing import Optional
from langgraph.graph import StateGraph, END
from src.graph.state import DesignValidationState
from src.utils.llm_client import OllamaClient
from src.agents.parser_agent import parse_design
from src.agents.materials_agent import analyze_materials
from src.agents.electrical_agent import analyze_electrical
from src.agents.conflict_agent import detect_conflicts
from src.agents.modification_agent import suggest_modifications

logger = logging.getLogger(__name__)


class DesignValidatorGraph:
    """LangGraph workflow for design validation."""
    
    def __init__(self, llm: OllamaClient):
        """Initialize with LLM client."""
        self.llm = llm
        self.graph = self._build_graph()
        self.node_times = {}
    
    def _build_graph(self) -> StateGraph:
        """Build the LangGraph workflow."""
        graph = StateGraph(DesignValidationState)
        
        # Define nodes
        graph.add_node("parse_design", self._node_parse_design)
        graph.add_node("analyze_materials", self._node_analyze_materials)
        graph.add_node("analyze_electrical", self._node_analyze_electrical)
        graph.add_node("detect_conflicts", self._node_detect_conflicts)
        graph.add_node("suggest_modifications", self._node_suggest_modifications)
        graph.add_node("format_output", self._node_format_output)
        
        # Define edges
        graph.add_edge("parse_design", "analyze_materials")
        graph.add_edge("analyze_materials", "analyze_electrical")
        graph.add_edge("analyze_electrical", "detect_conflicts")
        
        # Conditional edge: if conflicts detected, suggest modifications
        graph.add_conditional_edges(
            "detect_conflicts",
            self._should_suggest_modifications,
            {
                True: "suggest_modifications",
                False: "format_output"
            }
        )
        
        graph.add_edge("suggest_modifications", "format_output")
        graph.add_edge("format_output", END)
        
        # Set entry point
        graph.set_entry_point("parse_design")
        
        return graph
    
    def _node_parse_design(self, state: DesignValidationState) -> DesignValidationState:
        """Parse agent node."""
        start = time.time()
        result = parse_design(state, self.llm)
        self.node_times["parse_design"] = time.time() - start
        return result
    
    def _node_analyze_materials(self, state: DesignValidationState) -> DesignValidationState:
        """Materials analysis node."""
        start = time.time()
        result = analyze_materials(state, self.llm)
        self.node_times["analyze_materials"] = time.time() - start
        return result
    
    def _node_analyze_electrical(self, state: DesignValidationState) -> DesignValidationState:
        """Electrical analysis node."""
        start = time.time()
        result = analyze_electrical(state, self.llm)
        self.node_times["analyze_electrical"] = time.time() - start
        return result
    
    def _node_detect_conflicts(self, state: DesignValidationState) -> DesignValidationState:
        """Conflict detection node."""
        start = time.time()
        result = detect_conflicts(state, self.llm)
        self.node_times["detect_conflicts"] = time.time() - start
        return result
    
    def _node_suggest_modifications(self, state: DesignValidationState) -> DesignValidationState:
        """Modification suggestion node."""
        start = time.time()
        result = suggest_modifications(state, self.llm)
        self.node_times["suggest_modifications"] = time.time() - start
        return result
    
    def _node_format_output(self, state: DesignValidationState) -> DesignValidationState:
        """Format final JSON report."""
        start = time.time()
        
        # Determine status
        if state.get("parse_error"):
            status = "failed"
        elif state.get("domain_analysis_errors"):
            status = "partial_success"
        else:
            status = "success"
        
        # Build report
        report = {
            "metadata": {
                "timestamp": datetime.utcnow().isoformat() + "Z",
                "model_used": self.llm.model,
                "total_execution_time_seconds": sum(self.node_times.values()),
                "tokens_used": self.llm.get_token_count()
            },
            "parsed_design": state.get("parsed_design", {}),
            "domain_analyses": {
                "materials_science": state.get("materials_analysis", {}),
                "electrical_engineering": state.get("electrical_analysis", {})
            },
            "predicted_conflicts": state.get("detected_conflicts", []),
            "suggested_modifications": state.get("suggested_modifications", []),
            "validation_status": status,
            "error_log": state.get("domain_analysis_errors", [])
        }
        
        state["validation_report"] = report
        state["execution_metadata"] = {
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "model": self.llm.model,
            "node_execution_times": self.node_times,
            "tokens_used": self.llm.get_token_count(),
            "total_duration_sec": sum(self.node_times.values()),
            "error_log": state.get("domain_analysis_errors", [])
        }
        
        self.node_times["format_output"] = time.time() - start
        return state
    
    def _should_suggest_modifications(self, state: DesignValidationState) -> bool:
        """Decision: should we suggest modifications?"""
        conflicts = state.get("detected_conflicts", [])
        return len(conflicts) > 0
    
    def compile(self):
        """Compile the graph for execution."""
        return self.graph.compile()
    
    def invoke(self, input_state: DesignValidationState) -> DesignValidationState:
        """Execute the graph with given input."""
        compiled_graph = self.compile()
        logger.info("=" * 60)
        logger.info("Starting Design Validation Workflow")
        logger.info("=" * 60)
        
        result = compiled_graph.invoke(input_state)
        
        logger.info("=" * 60)
        logger.info(f"Workflow Complete - Status: {result['validation_report']['validation_status']}")
        logger.info("=" * 60)
        
        return result

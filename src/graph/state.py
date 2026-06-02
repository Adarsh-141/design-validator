"""
State definitions for the design validation workflow.
Uses TypedDict for strong typing and immutability tracking.
"""

from typing import TypedDict, Optional, List, Dict, Any
from datetime import datetime


class ParsedDesignEntity(TypedDict, total=False):
    """Extracted design entities from natural language."""
    material_type: str
    active_mechanism: str
    failure_modes: List[str]
    recovery_actions: List[str]
    key_constraints: List[str]


class MechanicalAnalysis(TypedDict, total=False):
    """Materials science domain analysis."""
    mechanical_properties: Dict[str, Any]
    rupture_thresholds: Dict[str, Any]
    failure_modes: List[str]
    risk_factors: List[str]


class ElectricalAnalysis(TypedDict, total=False):
    """Electrical engineering domain analysis."""
    conductivity_restoration: Dict[str, Any]
    resistance_changes: Dict[str, Any]
    failure_modes: List[str]
    risk_factors: List[str]


class DomainConflict(TypedDict, total=False):
    """Cross-domain conflict specification."""
    conflict_id: str
    description: str
    severity: int  # 1-10
    domain_a: str
    domain_b: str
    mechanism: str
    impact: str
    parameter_conflict: List[str]


class DesignModification(TypedDict, total=False):
    """Suggested design modification to resolve conflicts."""
    modification_id: str
    description: str
    addresses_conflicts: List[str]
    implementation_notes: str
    feasibility: str  # high/medium/low
    trade_off_analysis: str


class ExecutionMetadata(TypedDict, total=False):
    """Execution timing and resource tracking."""
    timestamp: str
    model: str
    node_execution_times: Dict[str, float]
    tokens_used: int
    total_duration_sec: float
    error_log: List[str]


class DesignValidationState(TypedDict, total=False):
    """Complete state for the design validation workflow."""
    # Input phase
    design_input: str

    # Parsing phase
    parsed_design: ParsedDesignEntity
    parse_error: Optional[str]

    # Domain analysis phase
    materials_analysis: MechanicalAnalysis
    electrical_analysis: ElectricalAnalysis
    domain_analysis_errors: List[str]

    # Conflict detection phase
    detected_conflicts: List[DomainConflict]

    # Modification phase
    suggested_modifications: List[DesignModification]

    # Output phase
    validation_report: Dict[str, Any]
    execution_metadata: ExecutionMetadata

"""
Output schemas for LLM responses.
Used to validate and parse structured outputs from agents.
"""

from pydantic import BaseModel, Field, validator
from typing import List, Dict, Any, Optional


class ParsedDesignSchema(BaseModel):
    """Validates parser agent output."""
    material_type: str = Field(..., description="Base material name")
    active_mechanism: str = Field(..., description="How the design achieves its function")
    failure_modes: List[str] = Field(..., description="Ways the design can fail")
    recovery_actions: List[str] = Field(..., description="Recovery mechanisms")
    key_constraints: List[str] = Field(..., description="Physical/chemical constraints")

    @validator('failure_modes', 'recovery_actions', 'key_constraints', pre=True)
    def ensure_list(cls, v):
        if isinstance(v, str):
            return [v]
        return v


class MaterialsAnalysisSchema(BaseModel):
    """Validates materials science agent output."""
    mechanical_properties: Dict[str, Any] = Field(..., description="Estimated mechanical properties")
    rupture_thresholds: Dict[str, Any] = Field(..., description="Component rupture levels")
    failure_modes: List[str] = Field(..., description="Predicted mechanical failures")
    risk_factors: List[str] = Field(..., description="Material-level concerns")


class ElectricalAnalysisSchema(BaseModel):
    """Validates electrical engineering agent output."""
    conductivity_restoration: Dict[str, Any] = Field(..., description="Conductivity restoration mechanism")
    resistance_changes: Dict[str, Any] = Field(..., description="Resistance before/after recovery")
    failure_modes: List[str] = Field(..., description="Predicted electrical failures")
    risk_factors: List[str] = Field(..., description="Electrical reliability concerns")


class ConflictSchema(BaseModel):
    """Validates individual conflict entry."""
    conflict_id: str = Field(..., description="Unique conflict identifier")
    description: str = Field(..., description="Short conflict description")
    severity: int = Field(..., ge=1, le=10, description="Severity rating 1-10")
    domain_a: str = Field(..., description="First domain involved")
    domain_b: str = Field(..., description="Second domain involved")
    mechanism: str = Field(..., description="How the conflict manifests")
    impact: str = Field(..., description="Impact if not resolved")
    parameter_conflict: List[str] = Field(default_factory=list, description="Parameters involved")


class ModificationSchema(BaseModel):
    """Validates individual modification entry."""
    modification_id: str = Field(..., description="Unique modification identifier")
    description: str = Field(..., description="Design modification description")
    addresses_conflicts: List[str] = Field(..., description="Conflict IDs this addresses")
    implementation_notes: str = Field(..., description="How to implement this modification")
    feasibility: str = Field(..., description="Feasibility: high/medium/low")
    trade_off_analysis: str = Field(..., description="Trade-offs and challenges")

    @validator('feasibility')
    def validate_feasibility(cls, v):
        if v not in ['high', 'medium', 'low']:
            raise ValueError('feasibility must be high, medium, or low')
        return v


class ConflictArraySchema(BaseModel):
    """Validates array of conflicts."""
    conflicts: List[ConflictSchema] = Field(..., description="List of detected conflicts")

    class Config:
        extra = 'ignore'


class ModificationArraySchema(BaseModel):
    """Validates array of modifications."""
    modifications: List[ModificationSchema] = Field(..., description="List of suggested modifications")

    class Config:
        extra = 'ignore'

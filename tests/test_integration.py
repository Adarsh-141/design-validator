"""
Integration tests for the design validator system.
"""

import pytest
import json
from src.graph.state import DesignValidationState
from src.graph.workflow import DesignValidatorGraph
from src.utils.llm_client import OllamaClient


class TestDesignValidator:
    """Test suite for design validator workflow."""
    
    @pytest.fixture
    def ollama_client(self):
        """Initialize Ollama client (requires Ollama running)."""
        try:
            client = OllamaClient(
                base_url="http://localhost:11434",
                model="mistral:7b",
                temperature=0.3,
                timeout=120
            )
            return client
        except Exception as e:
            pytest.skip(f"Ollama not available: {str(e)}")
    
    @pytest.fixture
    def validator_graph(self, ollama_client):
        """Initialize design validator graph."""
        return DesignValidatorGraph(ollama_client)
    
    def test_full_workflow_self_healing_conductor(self, validator_graph):
        """Test full workflow on self-healing conductor design."""
        design_input = (
            "A self-healing conductive material made from a polymer embedded with "
            "microcapsules containing a conductive liquid. When cracked, capsules "
            "rupture, liquid bridges the gap, restoring conductivity."
        )
        
        initial_state: DesignValidationState = {
            "design_input": design_input
        }
        
        result = validator_graph.invoke(initial_state)
        report = result.get("validation_report", {})
        
        # Assertions
        assert report.get("validation_status") == "success"
        assert "parsed_design" in report
        assert "domain_analyses" in report
        assert "predicted_conflicts" in report
        
        # Check parsed design
        parsed = report["parsed_design"]
        assert parsed.get("material_type")
        assert parsed.get("active_mechanism")
        assert len(parsed.get("failure_modes", [])) > 0
        
        # Check domain analyses
        analyses = report["domain_analyses"]
        assert "materials_science" in analyses
        assert "electrical_engineering" in analyses
        
        materials = analyses["materials_science"]
        assert "mechanical_properties" in materials
        assert "rupture_thresholds" in materials
        
        electrical = analyses["electrical_engineering"]
        assert "conductivity_restoration" in electrical
        assert "resistance_changes" in electrical
        
        # Check conflicts
        conflicts = report.get("predicted_conflicts", [])
        assert len(conflicts) > 0, "Should detect at least one conflict"
        
        for conflict in conflicts:
            assert "conflict_id" in conflict
            assert "severity" in conflict
            assert 1 <= conflict["severity"] <= 10
            assert "domain_a" in conflict
            assert "domain_b" in conflict
            assert "mechanism" in conflict
        
        # Check modifications
        mods = report.get("suggested_modifications", [])
        assert len(mods) > 0, "Should suggest modifications when conflicts exist"
        
        for mod in mods:
            assert "modification_id" in mod
            assert "addresses_conflicts" in mod
            assert "feasibility" in mod
            assert mod["feasibility"] in ["high", "medium", "low"]
    
    def test_metadata_present(self, validator_graph):
        """Test that execution metadata is recorded."""
        design_input = "A simple polymer with healing capsules."
        
        initial_state: DesignValidationState = {
            "design_input": design_input
        }
        
        result = validator_graph.invoke(initial_state)
        
        # Check execution metadata
        metadata = result.get("execution_metadata", {})
        assert "timestamp" in metadata
        assert "model" in metadata
        assert "node_execution_times" in metadata
        assert "tokens_used" in metadata
        assert "total_duration_sec" in metadata
        
        # Verify node times are reasonable
        node_times = metadata["node_execution_times"]
        for node, duration in node_times.items():
            assert duration > 0, f"Node {node} should have positive duration"
    
    def test_error_handling_empty_input(self, validator_graph):
        """Test error handling for empty design input."""
        initial_state: DesignValidationState = {
            "design_input": ""
        }
        
        result = validator_graph.invoke(initial_state)
        report = result.get("validation_report", {})
        
        assert report.get("validation_status") in ["failed", "partial_success"]
        assert len(report.get("error_log", [])) > 0
    
    def test_json_output_valid(self, validator_graph):
        """Test that output is valid JSON."""
        design_input = "A self-healing material with microcapsules."
        
        initial_state: DesignValidationState = {
            "design_input": design_input
        }
        
        result = validator_graph.invoke(initial_state)
        report = result.get("validation_report", {})
        
        # Should be serializable to JSON
        json_str = json.dumps(report)
        assert len(json_str) > 0
        
        # Should be deserializable back
        reparsed = json.loads(json_str)
        assert reparsed == report


class TestIndividualAgents:
    """Test individual agent functions."""
    
    @pytest.fixture
    def ollama_client(self):
        """Initialize Ollama client."""
        try:
            client = OllamaClient(
                base_url="http://localhost:11434",
                model="mistral:7b"
            )
            return client
        except:
            pytest.skip("Ollama not available")
    
    def test_parser_agent(self, ollama_client):
        """Test parser agent in isolation."""
        from src.agents.parser_agent import parse_design
        
        state: DesignValidationState = {
            "design_input": "A material with embedded capsules for healing."
        }
        
        result = parse_design(state, ollama_client)
        
        assert "parsed_design" in result
        parsed = result["parsed_design"]
        assert parsed.get("material_type")
        assert parsed.get("active_mechanism")
    
    def test_materials_agent(self, ollama_client):
        """Test materials agent in isolation."""
        from src.agents.materials_agent import analyze_materials
        
        state: DesignValidationState = {
            "parsed_design": {
                "material_type": "polymer",
                "active_mechanism": "microcapsules",
                "failure_modes": ["crack"],
                "recovery_actions": ["rupture"],
                "key_constraints": ["durability"]
            }
        }
        
        result = analyze_materials(state, ollama_client)
        
        assert "materials_analysis" in result
        analysis = result["materials_analysis"]
        assert "mechanical_properties" in analysis
        assert "rupture_thresholds" in analysis
    
    def test_electrical_agent(self, ollama_client):
        """Test electrical agent in isolation."""
        from src.agents.electrical_agent import analyze_electrical
        
        state: DesignValidationState = {
            "parsed_design": {
                "material_type": "polymer",
                "active_mechanism": "conductive liquid",
                "failure_modes": ["open circuit"],
                "recovery_actions": ["bridge formation"],
                "key_constraints": ["conductivity"]
            }
        }
        
        result = analyze_electrical(state, ollama_client)
        
        assert "electrical_analysis" in result
        analysis = result["electrical_analysis"]
        assert "conductivity_restoration" in analysis
        assert "resistance_changes" in analysis


class TestSchemaValidation:
    """Test Pydantic schema validation."""
    
    def test_parsed_design_schema(self):
        """Test ParsedDesignSchema validation."""
        from src.schemas.output_schemas import ParsedDesignSchema
        
        valid_data = {
            "material_type": "polymer",
            "active_mechanism": "microcapsules + liquid",
            "failure_modes": ["crack"],
            "recovery_actions": ["rupture"],
            "key_constraints": ["durability"]
        }
        
        schema = ParsedDesignSchema(**valid_data)
        assert schema.material_type == "polymer"
    
    def test_conflict_schema(self):
        """Test ConflictSchema validation."""
        from src.schemas.output_schemas import ConflictSchema
        
        valid_data = {
            "conflict_id": "CONF_001",
            "description": "Size trade-off",
            "severity": 8,
            "domain_a": "Materials",
            "domain_b": "Electrical",
            "mechanism": "Smaller equals...",
            "impact": "Cannot optimize both"
        }
        
        schema = ConflictSchema(**valid_data)
        assert schema.severity == 8
    
    def test_modification_schema(self):
        """Test ModificationSchema validation."""
        from src.schemas.output_schemas import ModificationSchema
        
        valid_data = {
            "modification_id": "MOD_001",
            "description": "Dual-size system",
            "addresses_conflicts": ["CONF_001"],
            "implementation_notes": "Use two sizes",
            "feasibility": "medium",
            "trade_off_analysis": "Adds complexity"
        }
        
        schema = ModificationSchema(**valid_data)
        assert schema.feasibility == "medium"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])

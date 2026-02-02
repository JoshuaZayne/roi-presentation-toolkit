"""
Agent Configuration for ROI Toolkit
===================================

Reusable agent for automating ROI analysis operations.
"""

import json
from typing import Dict, List, Optional, Any
from pathlib import Path


class ROIAgent:
    """Reusable agent for ROI analysis automation."""

    def __init__(self, config_path: Optional[str] = None):
        if config_path is None:
            config_path = Path(__file__).parent.parent / "config" / "config.json"
        with open(config_path, 'r') as f:
            self.config = json.load(f)
        self.context = {"prospect_name": None, "inputs": {}, "results": {}, "scenarios_calculated": []}

    def set_prospect(self, name: str, inputs: Optional[Dict] = None) -> None:
        self.context["prospect_name"] = name
        if inputs:
            self.context["inputs"] = inputs

    def calculate_roi(self, current_cost: float, efficiency_gain: float,
                      implementation_cost: float = 0, annual_license: float = 0,
                      years: int = 3, scenario: str = "moderate") -> Dict[str, Any]:
        from models.roi_model import ROIModel
        model = ROIModel()
        result = model.calculate(current_cost, efficiency_gain, implementation_cost, annual_license, years, scenario)
        self.context["inputs"] = {"current_cost": current_cost, "efficiency_gain": efficiency_gain,
                                   "implementation_cost": implementation_cost, "annual_license": annual_license, "years": years}
        self.context["results"][scenario] = result
        return result

    def get_context(self) -> Dict[str, Any]:
        return self.context.copy()

    def reset(self) -> None:
        self.context = {"prospect_name": None, "inputs": {}, "results": {}, "scenarios_calculated": []}


def create_agent(config_path: Optional[str] = None) -> ROIAgent:
    return ROIAgent(config_path)


AGENT_METADATA = {
    "name": "roi-presentation-agent",
    "version": "1.0.0",
    "description": "Generates ROI analyses and presentations for enterprise sales",
    "capabilities": ["roi_calculation", "tco_comparison", "sensitivity_analysis", "excel_export", "visualization"]
}

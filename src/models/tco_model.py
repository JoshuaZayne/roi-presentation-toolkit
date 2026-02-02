"""TCO Model - Total Cost of Ownership Analysis"""

from dataclasses import dataclass
from typing import Dict, List, Optional, Any
import json
from pathlib import Path


@dataclass
class TCOResult:
    """Results from TCO calculation."""
    current_state_tco: float
    future_state_tco: float
    tco_savings: float
    savings_percent: float
    years: int
    current_breakdown: Dict[str, float]
    future_breakdown: Dict[str, float]
    yearly_comparison: List[Dict[str, float]]
    hidden_costs_identified: Dict[str, float]

    def to_dict(self) -> dict:
        return {
            "current_state_tco": round(self.current_state_tco, 2),
            "future_state_tco": round(self.future_state_tco, 2),
            "tco_savings": round(self.tco_savings, 2),
            "savings_percent": round(self.savings_percent, 1),
            "years": self.years,
            "current_breakdown": {k: round(v, 2) for k, v in self.current_breakdown.items()},
            "future_breakdown": {k: round(v, 2) for k, v in self.future_breakdown.items()},
            "yearly_comparison": self.yearly_comparison,
            "hidden_costs_identified": {k: round(v, 2) for k, v in self.hidden_costs_identified.items()},
        }


class TCOModel:
    """
    Total Cost of Ownership calculation engine.

    Compares current state vs future state TCO over a configurable period,
    including often-overlooked hidden costs.
    """

    # Hidden cost categories as percentage of base costs
    HIDDEN_COST_FACTORS = {
        "training": {"initial_pct": 0.15, "annual_pct": 0.05},
        "maintenance": {"annual_pct": 0.18},
        "infrastructure": {"annual_pct": 0.10},
        "opportunity_cost": {"discount_rate": 0.08},
        "change_management": {"pct_of_implementation": 0.20},
        "data_migration": {"pct_of_implementation": 0.25},
        "productivity_loss": {"months": 3, "loss_pct": 0.15},
        "integration": {"annual_pct": 0.08},
    }

    def __init__(self, assumptions_path: Optional[str] = None):
        self.assumptions = self._load_assumptions(assumptions_path)

    def _load_assumptions(self, path: Optional[str]) -> dict:
        if path and Path(path).exists():
            with open(path, "r") as f:
                data = json.load(f)
                return data.get("hidden_costs", self.HIDDEN_COST_FACTORS)
        return self.HIDDEN_COST_FACTORS

    def calculate_current_state(
        self,
        annual_operations: float,
        annual_maintenance: float,
        annual_labor: float = 0,
        annual_infrastructure: float = 0,
        years: int = 5,
        include_hidden: bool = True,
        inflation_rate: float = 0.03
    ) -> Dict[str, Any]:
        """Calculate current state TCO."""
        base_annual = annual_operations + annual_maintenance + annual_labor + annual_infrastructure

        hidden_costs = {}
        if include_hidden:
            hidden_costs = {
                "unplanned_maintenance": base_annual * 0.12,
                "productivity_overhead": annual_labor * 0.20,
                "manual_workarounds": annual_operations * 0.15,
                "compliance_risk": annual_operations * 0.08,
            }

        yearly_costs = []
        cumulative = 0
        for year in range(1, years + 1):
            inflation_factor = (1 + inflation_rate) ** (year - 1)
            year_base = base_annual * inflation_factor
            year_hidden = sum(hidden_costs.values()) * inflation_factor if include_hidden else 0
            year_total = year_base + year_hidden
            cumulative += year_total
            yearly_costs.append({
                "year": year,
                "base_cost": round(year_base, 2),
                "hidden_cost": round(year_hidden, 2),
                "total": round(year_total, 2),
                "cumulative": round(cumulative, 2),
            })

        return {
            "total_tco": cumulative,
            "base_annual": base_annual,
            "hidden_annual": sum(hidden_costs.values()) if include_hidden else 0,
            "breakdown": {
                "operations": annual_operations * years,
                "maintenance": annual_maintenance * years,
                "labor": annual_labor * years,
                "infrastructure": annual_infrastructure * years,
                **{f"hidden_{k}": v * years for k, v in hidden_costs.items()},
            },
            "yearly_projection": yearly_costs,
        }

    def calculate_future_state(
        self,
        implementation_cost: float,
        annual_license: float,
        annual_support: float = 0,
        years: int = 5,
        include_hidden: bool = True,
        efficiency_savings: float = 0,
        inflation_rate: float = 0.03
    ) -> Dict[str, Any]:
        """Calculate future state TCO with solution."""
        base_annual = annual_license + annual_support

        hidden_costs = {}
        if include_hidden:
            factors = self.assumptions
            hidden_costs = {
                "training_initial": implementation_cost * factors.get("training", {}).get("initial_pct", 0.15),
                "training_ongoing": annual_license * factors.get("training", {}).get("annual_pct", 0.05) * years,
                "change_management": implementation_cost * factors.get("change_management", {}).get("pct_of_implementation", 0.20),
                "data_migration": implementation_cost * factors.get("data_migration", {}).get("pct_of_implementation", 0.25),
                "integration_maintenance": annual_license * factors.get("integration", {}).get("annual_pct", 0.08) * years,
            }

        yearly_costs = []
        cumulative = implementation_cost
        year_0_hidden = hidden_costs.get("training_initial", 0) + \
                       hidden_costs.get("change_management", 0) + \
                       hidden_costs.get("data_migration", 0)
        cumulative += year_0_hidden if include_hidden else 0

        yearly_costs.append({
            "year": 0,
            "base_cost": round(implementation_cost, 2),
            "hidden_cost": round(year_0_hidden, 2),
            "savings": 0,
            "total": round(implementation_cost + year_0_hidden, 2),
            "cumulative": round(cumulative, 2),
        })

        for year in range(1, years + 1):
            inflation_factor = (1 + inflation_rate) ** (year - 1)
            year_base = base_annual * inflation_factor
            year_hidden = (hidden_costs.get("training_ongoing", 0) / years +
                          hidden_costs.get("integration_maintenance", 0) / years) if include_hidden else 0
            year_savings = efficiency_savings * inflation_factor
            year_net = year_base + year_hidden - year_savings
            cumulative += year_net
            yearly_costs.append({
                "year": year,
                "base_cost": round(year_base, 2),
                "hidden_cost": round(year_hidden, 2),
                "savings": round(year_savings, 2),
                "total": round(year_net, 2),
                "cumulative": round(cumulative, 2),
            })

        return {
            "total_tco": cumulative,
            "implementation_cost": implementation_cost,
            "base_annual": base_annual,
            "hidden_costs": hidden_costs if include_hidden else {},
            "breakdown": {
                "implementation": implementation_cost,
                "license": annual_license * years,
                "support": annual_support * years,
                **hidden_costs,
            },
            "yearly_projection": yearly_costs,
        }

    def compare(
        self,
        current_state: Dict[str, float],
        future_state: Dict[str, float],
        years: int = 5,
        include_hidden: bool = True
    ) -> TCOResult:
        """Compare current state TCO with future state TCO."""
        current = self.calculate_current_state(
            annual_operations=current_state.get("annual_operations", 0),
            annual_maintenance=current_state.get("annual_maintenance", 0),
            annual_labor=current_state.get("annual_labor", 0),
            annual_infrastructure=current_state.get("annual_infrastructure", 0),
            years=years,
            include_hidden=include_hidden,
        )

        future = self.calculate_future_state(
            implementation_cost=future_state.get("implementation", 0),
            annual_license=future_state.get("annual_license", 0),
            annual_support=future_state.get("annual_support", 0),
            years=years,
            include_hidden=include_hidden,
            efficiency_savings=future_state.get("efficiency_savings", 0),
        )

        current_tco = current["total_tco"]
        future_tco = future["total_tco"]
        tco_savings = current_tco - future_tco
        savings_pct = (tco_savings / current_tco * 100) if current_tco > 0 else 0

        yearly_comparison = []
        for year in range(years + 1):
            curr_year = current["yearly_projection"][year] if year < len(current["yearly_projection"]) else None
            fut_year = future["yearly_projection"][year] if year < len(future["yearly_projection"]) else None
            if curr_year and fut_year:
                yearly_comparison.append({
                    "year": year,
                    "current_cumulative": curr_year.get("cumulative", 0),
                    "future_cumulative": fut_year.get("cumulative", 0),
                    "cumulative_savings": curr_year.get("cumulative", 0) - fut_year.get("cumulative", 0),
                })

        hidden_identified = {}
        if include_hidden:
            for k, v in current["breakdown"].items():
                if k.startswith("hidden_"):
                    hidden_identified[f"current_{k}"] = v
            for k, v in future.get("hidden_costs", {}).items():
                hidden_identified[f"future_{k}"] = v

        return TCOResult(
            current_state_tco=current_tco,
            future_state_tco=future_tco,
            tco_savings=tco_savings,
            savings_percent=savings_pct,
            years=years,
            current_breakdown=current["breakdown"],
            future_breakdown=future["breakdown"],
            yearly_comparison=yearly_comparison,
            hidden_costs_identified=hidden_identified,
        )

    def get_hidden_cost_summary(self, include_hidden: bool = True) -> Dict[str, str]:
        """Get descriptions of hidden cost categories."""
        if not include_hidden:
            return {}
        return {
            "training": "Initial and ongoing user training, certification costs",
            "change_management": "Communication, stakeholder management, adoption programs",
            "data_migration": "Data cleansing, transformation, validation, historical load",
            "integration_maintenance": "Ongoing integration updates and compatibility",
            "productivity_loss": "Temporary productivity dip during transition",
            "unplanned_maintenance": "Emergency fixes, unscheduled downtime costs",
            "compliance_risk": "Potential audit findings, regulatory penalties",
        }

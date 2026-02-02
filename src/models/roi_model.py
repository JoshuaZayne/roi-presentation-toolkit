"""ROI Model - Core Return on Investment Calculations"""

from dataclasses import dataclass
from typing import Dict, List, Optional
from enum import Enum
import json
from pathlib import Path

try:
    from scipy import optimize
except ImportError:
    optimize = None


class ScenarioType(Enum):
    CONSERVATIVE = "conservative"
    MODERATE = "moderate"
    AGGRESSIVE = "aggressive"


@dataclass
class ROIScenario:
    """Configuration for an ROI scenario."""
    name: str
    implementation_multiplier: float
    efficiency_multiplier: float
    discount_rate: float
    adoption_rate: float
    benefit_realization: Dict[int, float]

    @classmethod
    def from_assumptions(cls, scenario_type: ScenarioType, assumptions: dict):
        impl_costs = assumptions.get("implementation_costs", {})
        fin_params = assumptions.get("financial_parameters", {})
        risk_adj = assumptions.get("risk_adjustments", {})
        eff_mult = 1.0 if scenario_type == ScenarioType.MODERATE else (
            0.8 if scenario_type == ScenarioType.CONSERVATIVE else 1.15)
        return cls(
            name=scenario_type.value,
            implementation_multiplier=impl_costs.get(scenario_type.value, 1.2),
            efficiency_multiplier=eff_mult,
            discount_rate=fin_params.get("discount_rate", {}).get(scenario_type.value, 0.10),
            adoption_rate=risk_adj.get("adoption_rate", {}).get(scenario_type.value, 0.85),
            benefit_realization={
                1: risk_adj.get("benefit_realization_timeline", {}).get("year_1_pct", 0.5),
                2: risk_adj.get("benefit_realization_timeline", {}).get("year_2_pct", 0.85),
                3: risk_adj.get("benefit_realization_timeline", {}).get("year_3_pct", 1.0),
            }
        )


@dataclass
class ROIResult:
    """Results from ROI calculation."""
    scenario_name: str
    total_investment: float
    implementation_cost: float
    annual_license: float
    annual_savings: float
    net_annual_benefit: float
    three_year_net_benefit: float
    roi_percent: float
    payback_months: float
    npv: float
    irr: Optional[float]
    yearly_cash_flows: List[float]
    yearly_benefits: List[float]
    yearly_costs: List[float]

    def to_dict(self) -> dict:
        return {
            "scenario_name": self.scenario_name,
            "total_investment": round(self.total_investment, 2),
            "implementation_cost": round(self.implementation_cost, 2),
            "annual_license": round(self.annual_license, 2),
            "annual_savings": round(self.annual_savings, 2),
            "net_annual_benefit": round(self.net_annual_benefit, 2),
            "three_year_net_benefit": round(self.three_year_net_benefit, 2),
            "roi_percent": round(self.roi_percent, 1),
            "payback_months": round(self.payback_months, 1),
            "npv": round(self.npv, 2),
            "irr": round(self.irr * 100, 1) if self.irr else None,
            "yearly_cash_flows": [round(cf, 2) for cf in self.yearly_cash_flows],
            "yearly_benefits": [round(b, 2) for b in self.yearly_benefits],
            "yearly_costs": [round(c, 2) for c in self.yearly_costs],
        }


class ROIModel:
    """Core ROI calculation engine."""

    def __init__(self, assumptions_path: Optional[str] = None):
        self.assumptions = self._load_assumptions(assumptions_path)
        self.scenarios: Dict[str, ROIScenario] = {}
        self._initialize_scenarios()

    def _load_assumptions(self, path: Optional[str]) -> dict:
        if path and Path(path).exists():
            with open(path, "r") as f:
                return json.load(f)
        return {
            "implementation_costs": {"conservative": 1.5, "moderate": 1.2, "aggressive": 1.0},
            "financial_parameters": {"discount_rate": {"conservative": 0.12, "moderate": 0.10, "aggressive": 0.08}},
            "risk_adjustments": {
                "adoption_rate": {"conservative": 0.70, "moderate": 0.85, "aggressive": 0.95},
                "benefit_realization_timeline": {"year_1_pct": 0.50, "year_2_pct": 0.85, "year_3_pct": 1.00}
            }
        }

    def _initialize_scenarios(self):
        for scenario_type in ScenarioType:
            self.scenarios[scenario_type.value] = ROIScenario.from_assumptions(
                scenario_type, self.assumptions)

    def calculate(self, current_annual_cost: float, efficiency_gain: float,
                  annual_license: float, implementation_cost: Optional[float] = None,
                  years: int = 3, scenario: str = "moderate",
                  industry_multiplier: float = 1.0) -> ROIResult:
        """Calculate ROI for given inputs."""
        config = self.scenarios.get(scenario, self.scenarios["moderate"])

        if implementation_cost is None:
            implementation_cost = annual_license * config.implementation_multiplier

        adjusted_efficiency = efficiency_gain * config.efficiency_multiplier * industry_multiplier
        annual_savings = current_annual_cost * adjusted_efficiency * config.adoption_rate
        net_annual_benefit = annual_savings - annual_license
        total_investment = implementation_cost + (annual_license * years)

        yearly_benefits = [0]
        yearly_costs = [implementation_cost]
        yearly_cash_flows = [-implementation_cost]

        for year in range(1, years + 1):
            realization = config.benefit_realization.get(year, 1.0)
            benefit = annual_savings * realization
            yearly_benefits.append(benefit)
            yearly_costs.append(annual_license)
            yearly_cash_flows.append(benefit - annual_license)

        three_year_net_benefit = sum(yearly_benefits) - sum(yearly_costs)
        roi_percent = (three_year_net_benefit / total_investment) * 100 if total_investment > 0 else 0
        payback_months = self._calculate_payback(
            implementation_cost, annual_license, annual_savings, config.benefit_realization)
        npv = self._calculate_npv(yearly_cash_flows, config.discount_rate)
        irr = self._calculate_irr(yearly_cash_flows)

        return ROIResult(
            scenario_name=config.name,
            total_investment=total_investment,
            implementation_cost=implementation_cost,
            annual_license=annual_license,
            annual_savings=annual_savings,
            net_annual_benefit=net_annual_benefit,
            three_year_net_benefit=three_year_net_benefit,
            roi_percent=roi_percent,
            payback_months=payback_months,
            npv=npv,
            irr=irr,
            yearly_cash_flows=yearly_cash_flows,
            yearly_benefits=yearly_benefits,
            yearly_costs=yearly_costs
        )

    def calculate_all_scenarios(self, current_annual_cost: float, efficiency_gain: float,
                                annual_license: float, implementation_cost: Optional[float] = None,
                                years: int = 3, industry_multiplier: float = 1.0) -> Dict[str, ROIResult]:
        """Calculate ROI for all scenarios."""
        return {
            name: self.calculate(current_annual_cost, efficiency_gain, annual_license,
                                implementation_cost, years, name, industry_multiplier)
            for name in self.scenarios
        }

    def _calculate_payback(self, impl_cost: float, license_cost: float,
                           savings: float, realization: Dict[int, float]) -> float:
        """Calculate payback period in months."""
        if savings <= license_cost:
            return float("inf")
        cumulative = 0
        for month in range(1, 121):
            year = (month - 1) // 12 + 1
            cumulative += (savings * realization.get(year, 1.0)) / 12
            if cumulative >= impl_cost + (license_cost / 12 * month):
                return float(month)
        return float("inf")

    def _calculate_npv(self, cash_flows: List[float], rate: float) -> float:
        """Calculate Net Present Value."""
        return sum(cf / ((1 + rate) ** t) for t, cf in enumerate(cash_flows))

    def _calculate_irr(self, cash_flows: List[float]) -> Optional[float]:
        """Calculate Internal Rate of Return."""
        if optimize is None:
            return None
        def npv_at_rate(r):
            return sum(cf / ((1 + r) ** t) for t, cf in enumerate(cash_flows))
        try:
            return optimize.brentq(npv_at_rate, -0.99, 10.0)
        except (ValueError, RuntimeError):
            return None

    def get_efficiency_benchmarks(self, industry: str = None) -> dict:
        """Get efficiency gain benchmarks from assumptions."""
        benchmarks = self.assumptions.get("efficiency_gains", {})
        if industry:
            mult = self.assumptions.get("industry_multipliers", {}).get(industry, 1.0)
            return {
                cat: {k: v * mult if isinstance(v, float) else v for k, v in vals.items()}
                for cat, vals in benchmarks.items()
            }
        return benchmarks

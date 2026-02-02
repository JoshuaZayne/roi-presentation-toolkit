"""Sensitivity Analysis Module - Variable Impact and Monte Carlo Simulation"""

from dataclasses import dataclass
from typing import Dict, List, Any, Optional, Tuple
import numpy as np
from pathlib import Path


@dataclass
class SensitivityResult:
    """Results from sensitivity analysis."""
    variable: str
    base_value: float
    low_value: float
    high_value: float
    base_roi: float
    low_roi: float
    high_roi: float
    impact_range: float

    def to_dict(self) -> dict:
        return {
            "variable": self.variable,
            "base_value": round(self.base_value, 2),
            "low_value": round(self.low_value, 2),
            "high_value": round(self.high_value, 2),
            "base_roi": round(self.base_roi, 1),
            "low_roi": round(self.low_roi, 1),
            "high_roi": round(self.high_roi, 1),
            "impact_range": round(self.impact_range, 1),
        }


@dataclass
class MonteCarloResult:
    """Results from Monte Carlo simulation."""
    iterations: int
    roi_mean: float
    roi_std: float
    roi_median: float
    roi_p10: float
    roi_p50: float
    roi_p90: float
    probability_positive_roi: float
    probability_above_hurdle: float
    break_even_probability: float
    distribution: List[float]

    def to_dict(self) -> dict:
        return {
            "iterations": self.iterations,
            "roi_mean": round(self.roi_mean, 1),
            "roi_std": round(self.roi_std, 1),
            "roi_median": round(self.roi_median, 1),
            "roi_p10": round(self.roi_p10, 1),
            "roi_p50": round(self.roi_p50, 1),
            "roi_p90": round(self.roi_p90, 1),
            "probability_positive_roi": round(self.probability_positive_roi * 100, 1),
            "probability_above_hurdle": round(self.probability_above_hurdle * 100, 1),
            "break_even_probability": round(self.break_even_probability * 100, 1),
        }


class SensitivityAnalyzer:
    """
    Perform sensitivity analysis on ROI model inputs.

    Includes one-way sensitivity, tornado diagrams, and break-even analysis.
    """

    VARIABLE_LABELS = {
        "efficiency_gain": "Efficiency Gain",
        "annual_license": "Annual License Cost",
        "implementation_cost": "Implementation Cost",
        "current_annual_cost": "Current Annual Cost",
        "adoption_rate": "Adoption Rate",
        "discount_rate": "Discount Rate",
    }

    def __init__(self, roi_model=None):
        if roi_model is None:
            from .roi_model import ROIModel
            roi_model = ROIModel()
        self.model = roi_model

    def one_way_analysis(
        self,
        base_inputs: Dict[str, float],
        variable: str,
        range_pct: float = 0.2,
        steps: int = 5
    ) -> List[Dict[str, Any]]:
        """
        Perform one-way sensitivity analysis on a single variable.

        Args:
            base_inputs: Base case input values
            variable: Variable to vary
            range_pct: Range as percentage of base value (e.g., 0.2 = +/- 20%)
            steps: Number of steps in the range

        Returns:
            List of results at each step
        """
        base_value = base_inputs.get(variable, 0)
        if base_value == 0:
            return []

        results = []
        multipliers = np.linspace(1 - range_pct, 1 + range_pct, steps)

        for mult in multipliers:
            test_inputs = base_inputs.copy()
            test_inputs[variable] = base_value * mult

            result = self.model.calculate(
                current_annual_cost=test_inputs.get("current_annual_cost", 500000),
                efficiency_gain=test_inputs.get("efficiency_gain", 0.30),
                implementation_cost=test_inputs.get("implementation_cost"),
                annual_license=test_inputs.get("annual_license", 150000),
                years=int(test_inputs.get("years", 3)),
                scenario=test_inputs.get("scenario", "moderate"),
            )

            results.append({
                "multiplier": round(mult, 2),
                "percentage": round((mult - 1) * 100, 0),
                "variable": variable,
                "variable_label": self.VARIABLE_LABELS.get(variable, variable),
                "value": round(test_inputs[variable], 2),
                "roi_percent": result.roi_percent,
                "npv": result.npv,
                "payback_months": result.payback_months,
            })

        return results

    def tornado_analysis(
        self,
        base_inputs: Dict[str, float],
        variables: Optional[List[str]] = None,
        range_pct: float = 0.2
    ) -> List[SensitivityResult]:
        """
        Perform tornado diagram analysis - show impact of each variable.

        Returns variables sorted by impact range (largest first).
        """
        if variables is None:
            variables = ["efficiency_gain", "annual_license", "implementation_cost", "current_annual_cost"]

        results = []

        # Calculate base case ROI
        base_result = self.model.calculate(
            current_annual_cost=base_inputs.get("current_annual_cost", 500000),
            efficiency_gain=base_inputs.get("efficiency_gain", 0.30),
            implementation_cost=base_inputs.get("implementation_cost"),
            annual_license=base_inputs.get("annual_license", 150000),
            years=int(base_inputs.get("years", 3)),
        )
        base_roi = base_result.roi_percent

        for var in variables:
            base_value = base_inputs.get(var, 0)
            if base_value == 0:
                continue

            # Calculate low case
            low_inputs = base_inputs.copy()
            low_inputs[var] = base_value * (1 - range_pct)
            low_result = self.model.calculate(
                current_annual_cost=low_inputs.get("current_annual_cost", 500000),
                efficiency_gain=low_inputs.get("efficiency_gain", 0.30),
                implementation_cost=low_inputs.get("implementation_cost"),
                annual_license=low_inputs.get("annual_license", 150000),
                years=int(low_inputs.get("years", 3)),
            )

            # Calculate high case
            high_inputs = base_inputs.copy()
            high_inputs[var] = base_value * (1 + range_pct)
            high_result = self.model.calculate(
                current_annual_cost=high_inputs.get("current_annual_cost", 500000),
                efficiency_gain=high_inputs.get("efficiency_gain", 0.30),
                implementation_cost=high_inputs.get("implementation_cost"),
                annual_license=high_inputs.get("annual_license", 150000),
                years=int(high_inputs.get("years", 3)),
            )

            results.append(SensitivityResult(
                variable=self.VARIABLE_LABELS.get(var, var),
                base_value=base_value,
                low_value=base_value * (1 - range_pct),
                high_value=base_value * (1 + range_pct),
                base_roi=base_roi,
                low_roi=low_result.roi_percent,
                high_roi=high_result.roi_percent,
                impact_range=abs(high_result.roi_percent - low_result.roi_percent),
            ))

        # Sort by impact range (descending)
        results.sort(key=lambda x: x.impact_range, reverse=True)
        return results

    def break_even_analysis(
        self,
        base_inputs: Dict[str, float],
        variable: str = "efficiency_gain"
    ) -> Dict[str, Any]:
        """
        Find break-even point for a given variable.

        Returns the value at which ROI = 0%.
        """
        base_value = base_inputs.get(variable, 0)

        # Binary search for break-even point
        low_mult, high_mult = 0.0, 2.0

        for _ in range(50):  # Max iterations
            mid_mult = (low_mult + high_mult) / 2
            test_inputs = base_inputs.copy()
            test_inputs[variable] = base_value * mid_mult

            result = self.model.calculate(
                current_annual_cost=test_inputs.get("current_annual_cost", 500000),
                efficiency_gain=test_inputs.get("efficiency_gain", 0.30),
                implementation_cost=test_inputs.get("implementation_cost"),
                annual_license=test_inputs.get("annual_license", 150000),
                years=int(test_inputs.get("years", 3)),
            )

            if abs(result.roi_percent) < 0.5:  # Close enough to zero
                break
            elif result.roi_percent > 0:
                high_mult = mid_mult
            else:
                low_mult = mid_mult

        break_even_value = base_value * mid_mult

        return {
            "variable": variable,
            "variable_label": self.VARIABLE_LABELS.get(variable, variable),
            "base_value": round(base_value, 2),
            "break_even_value": round(break_even_value, 2),
            "break_even_multiplier": round(mid_mult, 3),
            "margin_of_safety": round((1 - mid_mult) * 100, 1) if mid_mult < 1 else round((mid_mult - 1) * 100, 1),
        }


class MonteCarloSimulator:
    """
    Monte Carlo simulation for ROI confidence intervals.

    Uses triangular distributions for input variables to model uncertainty.
    """

    def __init__(self, roi_model=None):
        if roi_model is None:
            from .roi_model import ROIModel
            roi_model = ROIModel()
        self.model = roi_model

    def simulate(
        self,
        base_inputs: Dict[str, float],
        iterations: int = 10000,
        hurdle_rate: float = 100.0,
        variable_ranges: Optional[Dict[str, Tuple[float, float]]] = None
    ) -> MonteCarloResult:
        """
        Run Monte Carlo simulation.

        Args:
            base_inputs: Base case input values
            iterations: Number of simulation iterations
            hurdle_rate: Minimum acceptable ROI % for success probability
            variable_ranges: Optional custom ranges for variables as (low_mult, high_mult)

        Returns:
            MonteCarloResult with distribution statistics
        """
        if variable_ranges is None:
            variable_ranges = {
                "efficiency_gain": (0.7, 1.3),
                "implementation_cost": (0.8, 1.4),
                "annual_license": (0.9, 1.1),
                "current_annual_cost": (0.9, 1.1),
            }

        roi_results = []

        for _ in range(iterations):
            # Generate random inputs using triangular distribution
            sim_inputs = base_inputs.copy()

            for var, (low_mult, high_mult) in variable_ranges.items():
                if var in base_inputs:
                    base_val = base_inputs[var]
                    # Triangular distribution centered on base
                    random_mult = np.random.triangular(low_mult, 1.0, high_mult)
                    sim_inputs[var] = base_val * random_mult

            result = self.model.calculate(
                current_annual_cost=sim_inputs.get("current_annual_cost", 500000),
                efficiency_gain=sim_inputs.get("efficiency_gain", 0.30),
                implementation_cost=sim_inputs.get("implementation_cost"),
                annual_license=sim_inputs.get("annual_license", 150000),
                years=int(sim_inputs.get("years", 3)),
            )

            roi_results.append(result.roi_percent)

        roi_array = np.array(roi_results)

        return MonteCarloResult(
            iterations=iterations,
            roi_mean=float(np.mean(roi_array)),
            roi_std=float(np.std(roi_array)),
            roi_median=float(np.median(roi_array)),
            roi_p10=float(np.percentile(roi_array, 10)),
            roi_p50=float(np.percentile(roi_array, 50)),
            roi_p90=float(np.percentile(roi_array, 90)),
            probability_positive_roi=float(np.sum(roi_array > 0) / len(roi_array)),
            probability_above_hurdle=float(np.sum(roi_array > hurdle_rate) / len(roi_array)),
            break_even_probability=float(np.sum(roi_array >= 0) / len(roi_array)),
            distribution=roi_results,
        )

    def confidence_interval(
        self,
        base_inputs: Dict[str, float],
        confidence: float = 0.90,
        iterations: int = 10000
    ) -> Dict[str, float]:
        """
        Calculate confidence interval for ROI.

        Returns:
            Dict with lower bound, upper bound, and confidence level
        """
        result = self.simulate(base_inputs, iterations=iterations)

        alpha = (1 - confidence) / 2
        lower_pct = alpha * 100
        upper_pct = (1 - alpha) * 100

        roi_array = np.array(result.distribution)

        return {
            "confidence_level": confidence,
            "lower_bound": round(float(np.percentile(roi_array, lower_pct)), 1),
            "upper_bound": round(float(np.percentile(roi_array, upper_pct)), 1),
            "median": round(result.roi_median, 1),
            "mean": round(result.roi_mean, 1),
        }


# Backward compatibility aliases
SensitivityAnalysis = SensitivityAnalyzer

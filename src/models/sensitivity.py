"""Sensitivity Analysis Module"""

from typing import Dict, List, Any
import numpy as np


class SensitivityAnalysis:
    """Perform sensitivity analysis on ROI inputs."""

    def one_way(self, base_inputs: Dict[str, float], variable: str,
                range_pct: float = 0.2) -> List[Dict[str, Any]]:
        from models.roi_model import ROIModel
        model = ROIModel()

        var_map = {
            'efficiency': 'efficiency_gain',
            'license': 'annual_license',
            'implementation': 'implementation_cost'
        }
        var_key = var_map.get(variable, variable)
        base_value = base_inputs.get(var_key, 0)

        results = []
        for mult, label in [(1 - range_pct, 'Low'), (1.0, 'Base'), (1 + range_pct, 'High')]:
            test_inputs = base_inputs.copy()
            test_inputs[var_key] = base_value * mult
            result = model.calculate(
                current_annual_cost=test_inputs.get('current_annual_cost', 500000),
                efficiency_gain=test_inputs.get('efficiency_gain', 0.30),
                implementation_cost=test_inputs.get('implementation_cost', 100000),
                annual_license=test_inputs.get('annual_license', 150000),
                years=test_inputs.get('years', 3)
            )
            results.append({
                'label': f"{label} ({int(mult*100)}%)",
                'value': test_inputs[var_key],
                'roi': result['roi_percent'],
                'payback': result['payback_months']
            })
        return results

    def monte_carlo(self, base_inputs: Dict[str, float], iterations: int = 1000) -> Dict[str, Any]:
        from models.roi_model import ROIModel
        model = ROIModel()

        roi_results = []
        for _ in range(iterations):
            eff = base_inputs['efficiency_gain'] * np.random.uniform(0.7, 1.3)
            result = model.calculate(
                current_annual_cost=base_inputs.get('current_annual_cost', 500000),
                efficiency_gain=eff,
                implementation_cost=base_inputs.get('implementation_cost', 100000),
                annual_license=base_inputs.get('annual_license', 150000),
                years=base_inputs.get('years', 3)
            )
            roi_results.append(result['roi_percent'])

        return {
            'roi_mean': np.mean(roi_results),
            'roi_std': np.std(roi_results),
            'roi_p5': np.percentile(roi_results, 5),
            'roi_p95': np.percentile(roi_results, 95),
            'prob_positive': sum(1 for r in roi_results if r > 100) / len(roi_results)
        }

    def tornado_data(self, base_inputs: Dict[str, float]) -> Dict[str, Dict]:
        variables = ['efficiency_gain', 'annual_license', 'implementation_cost']
        data = {}
        for var in variables:
            results = self.one_way(base_inputs, var, 0.2)
            data[var] = {'low': results[0]['roi'], 'base': results[1]['roi'], 'high': results[2]['roi']}
        return data

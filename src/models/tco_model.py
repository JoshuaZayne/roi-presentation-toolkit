"""TCO Model - Total Cost of Ownership Comparison"""

from typing import Dict, Any


class TCOModel:
    """Calculate and compare Total Cost of Ownership."""

    def __init__(self):
        self.hidden_cost_multiplier = 0.30  # 30% hidden costs

    def compare(self, current_state: Dict[str, float], future_state: Dict[str, float],
                years: int = 5, include_hidden: bool = True) -> Dict[str, Any]:
        current_annual = sum([
            current_state.get('annual_operations', 0),
            current_state.get('annual_maintenance', 0)
        ])

        if include_hidden:
            current_hidden = current_annual * self.hidden_cost_multiplier
            current_annual += current_hidden
        else:
            current_hidden = 0

        current_tco = current_annual * years

        future_annual = sum([
            future_state.get('annual_license', 0),
            future_state.get('annual_support', 0)
        ])
        future_tco = future_state.get('implementation', 0) + (future_annual * years)

        tco_savings = current_tco - future_tco
        savings_percent = (tco_savings / current_tco * 100) if current_tco > 0 else 0

        return {
            'current_tco': round(current_tco, 2),
            'future_tco': round(future_tco, 2),
            'tco_savings': round(tco_savings, 2),
            'savings_percent': round(savings_percent, 1),
            'current_hidden': round(current_hidden * years, 2),
            'years': years
        }

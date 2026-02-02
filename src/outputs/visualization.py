"""Visualization Module - Plotly Charts"""
from typing import Dict, Any, List
import plotly.graph_objects as go

class ChartGenerator:
    """Generate interactive Plotly visualizations."""

    def roi_waterfall(self, result: Dict[str, Any]) -> go.Figure:
        labels = ['Current Cost', 'Savings', 'License Cost', 'Net Benefit']
        values = [
            result.get('current_annual_cost', 500000),
            result.get('annual_savings', 150000),
            -result.get('annual_license', 100000),
            result.get('net_annual_benefit', 50000)
        ]
        fig = go.Figure(go.Waterfall(
            name="ROI", orientation="v",
            measure=["absolute", "relative", "relative", "total"],
            x=labels, y=values,
            connector={"line": {"color": "rgb(63, 63, 63)"}}
        ))
        fig.update_layout(title="ROI Waterfall Analysis", showlegend=False)
        return fig

    def tco_comparison(self, result: Dict[str, Any]) -> go.Figure:
        fig = go.Figure()
        fig.add_trace(go.Bar(name='Current State', x=['TCO'],
                             y=[result.get('current_tco', 2000000)], marker_color='#dc3545'))
        fig.add_trace(go.Bar(name='Future State', x=['TCO'],
                             y=[result.get('future_tco', 1500000)], marker_color='#28a745'))
        fig.update_layout(title="TCO Comparison", barmode='group')
        return fig

    def payback_timeline(self, result: Dict[str, Any]) -> go.Figure:
        months = list(range(37))
        cumulative = [-result.get('total_investment', 100000)]
        monthly_benefit = result.get('net_annual_benefit', 50000) / 12
        for _ in range(36):
            cumulative.append(cumulative[-1] + monthly_benefit)

        fig = go.Figure()
        fig.add_trace(go.Scatter(x=months, y=cumulative, mode='lines', name='Cumulative Benefit',
                                  line=dict(color='#1F4E79', width=2)))
        fig.add_hline(y=0, line_dash="dash", line_color="red", annotation_text="Break-even")
        fig.update_layout(title="Payback Timeline", xaxis_title="Months", yaxis_title="Cumulative ($)")
        return fig

    def tornado_diagram(self, sensitivity_data: Dict[str, Dict]) -> go.Figure:
        variables = list(sensitivity_data.keys())
        low_vals = [sensitivity_data[v]['low'] - sensitivity_data[v]['base'] for v in variables]
        high_vals = [sensitivity_data[v]['high'] - sensitivity_data[v]['base'] for v in variables]

        fig = go.Figure()
        fig.add_trace(go.Bar(name='Downside', y=variables, x=low_vals, orientation='h', marker_color='#dc3545'))
        fig.add_trace(go.Bar(name='Upside', y=variables, x=high_vals, orientation='h', marker_color='#28a745'))
        fig.update_layout(title="Sensitivity Tornado Diagram", barmode='overlay', xaxis_title="ROI Change (%)")
        return fig

    def monte_carlo_distribution(self, roi_values: List[float]) -> go.Figure:
        fig = go.Figure(go.Histogram(x=roi_values, nbinsx=50, marker_color='#1F4E79'))
        fig.add_vline(x=100, line_dash="dash", line_color="red", annotation_text="100% ROI")
        fig.update_layout(title="Monte Carlo ROI Distribution", xaxis_title="ROI (%)", yaxis_title="Frequency")
        return fig

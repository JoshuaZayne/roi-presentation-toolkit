"""Visualization Module - Interactive Plotly Charts for ROI Presentations"""

from typing import Dict, Any, List, Optional
from pathlib import Path
import json

try:
    import plotly.graph_objects as go
    from plotly.subplots import make_subplots
    PLOTLY_AVAILABLE = True
except ImportError:
    PLOTLY_AVAILABLE = False


class ChartGenerator:
    """
    Generate interactive Plotly visualizations for ROI presentations.

    Includes:
    - ROI Waterfall Chart
    - TCO Comparison Bar Chart
    - Payback Period Timeline
    - Sensitivity Tornado Diagram
    - Monte Carlo Distribution
    """

    # Professional color scheme
    COLORS = {
        "primary": "#1F4E79",
        "secondary": "#4472C4",
        "positive": "#70AD47",
        "negative": "#C00000",
        "neutral": "#FFC000",
        "gray": "#808080",
        "light_gray": "#D9D9D9",
    }

    CHART_THEME = {
        "font_family": "Arial, sans-serif",
        "title_font_size": 16,
        "axis_font_size": 12,
        "background_color": "white",
        "grid_color": "#E5E5E5",
    }

    def __init__(self, config_path: Optional[str] = None):
        if not PLOTLY_AVAILABLE:
            raise ImportError("plotly required. Install: pip install plotly")

        self.config = self._load_config(config_path)

    def _load_config(self, path: Optional[str]) -> dict:
        if path and Path(path).exists():
            with open(path, "r") as f:
                return json.load(f).get("chart_settings", {})
        return {
            "theme": "plotly_white",
            "default_width": 900,
            "default_height": 600,
        }

    def _apply_layout(self, fig: go.Figure, title: str, **kwargs) -> go.Figure:
        """Apply consistent layout styling to a figure."""
        layout_updates = {
            "title": {
                "text": title,
                "font": {"size": self.CHART_THEME["title_font_size"], "family": self.CHART_THEME["font_family"]},
                "x": 0.5,
                "xanchor": "center",
            },
            "font": {"family": self.CHART_THEME["font_family"], "size": self.CHART_THEME["axis_font_size"]},
            "paper_bgcolor": self.CHART_THEME["background_color"],
            "plot_bgcolor": self.CHART_THEME["background_color"],
            "width": self.config.get("default_width", 900),
            "height": self.config.get("default_height", 600),
            "margin": {"l": 80, "r": 40, "t": 80, "b": 60},
        }
        layout_updates.update(kwargs)
        fig.update_layout(**layout_updates)
        return fig

    def roi_waterfall(self, roi_result: Dict[str, Any], title: str = "ROI Value Creation") -> go.Figure:
        """
        Create waterfall chart showing ROI value creation.

        Shows how current costs transform into net benefits through efficiency gains.
        """
        # Get values from result (handle both dict and object)
        if hasattr(roi_result, 'to_dict'):
            data = roi_result.to_dict()
        else:
            data = roi_result

        current_cost = data.get('annual_savings', 0) / data.get('efficiency_gain', 0.3) if data.get('efficiency_gain') else 500000
        annual_savings = data.get('annual_savings', 150000)
        annual_license = data.get('annual_license', 100000)
        net_benefit = data.get('net_annual_benefit', 50000)

        # Build waterfall data
        labels = [
            "Current Operations",
            "Efficiency Savings",
            "License Cost",
            "Net Annual Benefit"
        ]
        values = [current_cost, annual_savings, -annual_license, 0]
        measure = ["absolute", "relative", "relative", "total"]

        # Colors based on positive/negative
        colors = [
            self.COLORS["gray"],
            self.COLORS["positive"],
            self.COLORS["negative"],
            self.COLORS["primary"]
        ]

        fig = go.Figure(go.Waterfall(
            name="Value",
            orientation="v",
            measure=measure,
            x=labels,
            y=values,
            textposition="outside",
            text=[f"${v:,.0f}" if v != 0 else f"${net_benefit:,.0f}" for v in values],
            connector={"line": {"color": self.COLORS["light_gray"], "width": 2}},
            decreasing={"marker": {"color": self.COLORS["negative"]}},
            increasing={"marker": {"color": self.COLORS["positive"]}},
            totals={"marker": {"color": self.COLORS["primary"]}},
        ))

        fig = self._apply_layout(
            fig, title,
            yaxis_title="Annual Amount ($)",
            yaxis_tickformat="$,.0f",
            showlegend=False,
        )

        return fig

    def tco_comparison(
        self,
        tco_result: Dict[str, Any],
        title: str = "Total Cost of Ownership Comparison"
    ) -> go.Figure:
        """
        Create side-by-side bar chart comparing current vs future TCO.
        """
        if hasattr(tco_result, 'to_dict'):
            data = tco_result.to_dict()
        else:
            data = tco_result

        current_tco = data.get('current_state_tco', 2000000)
        future_tco = data.get('future_state_tco', 1500000)
        savings = data.get('tco_savings', 500000)
        years = data.get('years', 5)

        fig = go.Figure()

        # Current State bar
        fig.add_trace(go.Bar(
            name='Current State',
            x=['Current State'],
            y=[current_tco],
            marker_color=self.COLORS["negative"],
            text=[f"${current_tco:,.0f}"],
            textposition='outside',
        ))

        # Future State bar
        fig.add_trace(go.Bar(
            name='Future State',
            x=['Future State'],
            y=[future_tco],
            marker_color=self.COLORS["positive"],
            text=[f"${future_tco:,.0f}"],
            textposition='outside',
        ))

        # Add savings annotation
        fig.add_annotation(
            x=0.5, y=max(current_tco, future_tco) * 1.1,
            text=f"<b>{years}-Year Savings: ${savings:,.0f}</b>",
            showarrow=False,
            font={"size": 14, "color": self.COLORS["positive"]},
            xref="paper", yref="y",
        )

        fig = self._apply_layout(
            fig, title,
            yaxis_title=f"{years}-Year Total Cost ($)",
            yaxis_tickformat="$,.0f",
            showlegend=True,
            legend={"orientation": "h", "yanchor": "bottom", "y": 1.02},
        )

        return fig

    def payback_timeline(
        self,
        roi_result: Dict[str, Any],
        title: str = "Payback Period Analysis"
    ) -> go.Figure:
        """
        Create line chart showing cumulative cash flow and payback point.
        """
        if hasattr(roi_result, 'to_dict'):
            data = roi_result.to_dict()
        else:
            data = roi_result

        implementation_cost = data.get('implementation_cost', 100000)
        net_annual_benefit = data.get('net_annual_benefit', 50000)
        payback_months = data.get('payback_months', 24)
        years = 3

        # Generate monthly cumulative cash flow
        months = list(range((years * 12) + 1))
        cumulative = [-implementation_cost]
        monthly_benefit = net_annual_benefit / 12

        for month in range(1, len(months)):
            # Apply benefit realization curve (ramp up in year 1)
            if month <= 12:
                realization = 0.5 + (0.5 * month / 12)  # Ramp from 50% to 100%
            else:
                realization = 1.0
            cumulative.append(cumulative[-1] + (monthly_benefit * realization))

        fig = go.Figure()

        # Cumulative cash flow line
        fig.add_trace(go.Scatter(
            x=months,
            y=cumulative,
            mode='lines',
            name='Cumulative Cash Flow',
            line={"color": self.COLORS["primary"], "width": 3},
            fill='tozeroy',
            fillcolor='rgba(31, 78, 121, 0.1)',
        ))

        # Break-even line
        fig.add_hline(
            y=0,
            line_dash="dash",
            line_color=self.COLORS["gray"],
            annotation_text="Break-even",
            annotation_position="bottom right",
        )

        # Payback point marker
        if payback_months < len(months) and payback_months != float('inf'):
            payback_value = cumulative[int(payback_months)] if int(payback_months) < len(cumulative) else 0
            fig.add_trace(go.Scatter(
                x=[payback_months],
                y=[payback_value],
                mode='markers+text',
                name='Payback Point',
                marker={"size": 15, "color": self.COLORS["positive"], "symbol": "star"},
                text=[f"Month {int(payback_months)}"],
                textposition='top center',
            ))

        fig = self._apply_layout(
            fig, title,
            xaxis_title="Months",
            yaxis_title="Cumulative Cash Flow ($)",
            yaxis_tickformat="$,.0f",
            showlegend=True,
            legend={"orientation": "h", "yanchor": "bottom", "y": 1.02},
        )

        return fig

    def tornado_diagram(
        self,
        sensitivity_results: List[Any],
        title: str = "Sensitivity Analysis - Impact on ROI"
    ) -> go.Figure:
        """
        Create tornado diagram showing variable sensitivity impact.
        """
        if not sensitivity_results:
            return go.Figure()

        # Process results
        variables = []
        low_impacts = []
        high_impacts = []
        base_roi = 0

        for result in sensitivity_results:
            if hasattr(result, 'to_dict'):
                data = result.to_dict()
            else:
                data = result

            variables.append(data.get('variable', 'Unknown'))
            base = data.get('base_roi', 100)
            base_roi = base
            low_impacts.append(data.get('low_roi', base) - base)
            high_impacts.append(data.get('high_roi', base) - base)

        # Sort by impact range (largest first)
        sorted_indices = sorted(range(len(variables)),
                               key=lambda i: abs(high_impacts[i]) + abs(low_impacts[i]),
                               reverse=True)

        variables = [variables[i] for i in sorted_indices]
        low_impacts = [low_impacts[i] for i in sorted_indices]
        high_impacts = [high_impacts[i] for i in sorted_indices]

        fig = go.Figure()

        # Negative impact bars (left side)
        fig.add_trace(go.Bar(
            name='Downside (-20%)',
            y=variables,
            x=low_impacts,
            orientation='h',
            marker_color=self.COLORS["negative"],
            text=[f"{v:+.1f}%" for v in low_impacts],
            textposition='outside',
        ))

        # Positive impact bars (right side)
        fig.add_trace(go.Bar(
            name='Upside (+20%)',
            y=variables,
            x=high_impacts,
            orientation='h',
            marker_color=self.COLORS["positive"],
            text=[f"{v:+.1f}%" for v in high_impacts],
            textposition='outside',
        ))

        # Base case line
        fig.add_vline(
            x=0,
            line_width=2,
            line_color=self.COLORS["gray"],
            annotation_text=f"Base ROI: {base_roi:.1f}%",
            annotation_position="top",
        )

        fig = self._apply_layout(
            fig, title,
            xaxis_title="Change in ROI (%)",
            barmode='overlay',
            showlegend=True,
            legend={"orientation": "h", "yanchor": "bottom", "y": 1.02},
            height=max(400, len(variables) * 50 + 200),
        )

        return fig

    def monte_carlo_distribution(
        self,
        monte_carlo_result: Any,
        title: str = "Monte Carlo Simulation - ROI Distribution"
    ) -> go.Figure:
        """
        Create histogram showing Monte Carlo ROI distribution.
        """
        if hasattr(monte_carlo_result, 'distribution'):
            roi_values = monte_carlo_result.distribution
            mean_roi = monte_carlo_result.roi_mean
            p10 = monte_carlo_result.roi_p10
            p90 = monte_carlo_result.roi_p90
        elif isinstance(monte_carlo_result, dict):
            roi_values = monte_carlo_result.get('distribution', [])
            mean_roi = monte_carlo_result.get('roi_mean', 100)
            p10 = monte_carlo_result.get('roi_p10', 50)
            p90 = monte_carlo_result.get('roi_p90', 150)
        else:
            roi_values = monte_carlo_result
            mean_roi = sum(roi_values) / len(roi_values) if roi_values else 100
            p10 = sorted(roi_values)[int(len(roi_values) * 0.1)] if roi_values else 50
            p90 = sorted(roi_values)[int(len(roi_values) * 0.9)] if roi_values else 150

        fig = go.Figure()

        # Histogram
        fig.add_trace(go.Histogram(
            x=roi_values,
            nbinsx=50,
            marker_color=self.COLORS["secondary"],
            opacity=0.75,
            name="ROI Distribution",
        ))

        # Mean line
        fig.add_vline(
            x=mean_roi,
            line_width=3,
            line_color=self.COLORS["primary"],
            annotation_text=f"Mean: {mean_roi:.1f}%",
            annotation_position="top right",
        )

        # 100% ROI threshold
        fig.add_vline(
            x=100,
            line_dash="dash",
            line_width=2,
            line_color=self.COLORS["positive"],
            annotation_text="100% ROI",
            annotation_position="top left",
        )

        # Confidence interval shading
        fig.add_vrect(
            x0=p10, x1=p90,
            fillcolor=self.COLORS["primary"],
            opacity=0.1,
            line_width=0,
            annotation_text=f"80% CI: {p10:.0f}% - {p90:.0f}%",
            annotation_position="top left",
        )

        fig = self._apply_layout(
            fig, title,
            xaxis_title="ROI (%)",
            yaxis_title="Frequency",
            showlegend=False,
        )

        return fig

    def save_chart(self, fig: go.Figure, output_path: str, format: str = "html") -> str:
        """
        Save chart to file.

        Args:
            fig: Plotly figure
            output_path: Output file path
            format: Output format ('html', 'png', 'pdf', 'svg')

        Returns:
            Path to saved file
        """
        Path(output_path).parent.mkdir(parents=True, exist_ok=True)

        if format == "html":
            fig.write_html(output_path)
        elif format in ["png", "pdf", "svg", "jpeg"]:
            fig.write_image(output_path)
        else:
            raise ValueError(f"Unsupported format: {format}")

        return output_path

    def create_dashboard(
        self,
        roi_result: Dict[str, Any],
        tco_result: Optional[Dict[str, Any]] = None,
        sensitivity_results: Optional[List] = None,
        monte_carlo_result: Optional[Any] = None,
    ) -> go.Figure:
        """
        Create a multi-chart dashboard combining all visualizations.
        """
        # Determine number of rows based on available data
        num_charts = 2  # Always have waterfall and payback
        if tco_result:
            num_charts += 1
        if sensitivity_results:
            num_charts += 1
        if monte_carlo_result:
            num_charts += 1

        rows = (num_charts + 1) // 2
        fig = make_subplots(
            rows=rows, cols=2,
            subplot_titles=[
                "ROI Value Creation",
                "Payback Timeline",
                "TCO Comparison" if tco_result else "",
                "Sensitivity Analysis" if sensitivity_results else "",
            ][:num_charts],
            vertical_spacing=0.12,
            horizontal_spacing=0.1,
        )

        # Add waterfall
        waterfall = self.roi_waterfall(roi_result)
        for trace in waterfall.data:
            fig.add_trace(trace, row=1, col=1)

        # Add payback
        payback = self.payback_timeline(roi_result)
        for trace in payback.data:
            fig.add_trace(trace, row=1, col=2)

        # Add TCO if available
        chart_idx = 3
        if tco_result:
            tco = self.tco_comparison(tco_result)
            row, col = (chart_idx + 1) // 2, ((chart_idx - 1) % 2) + 1
            for trace in tco.data:
                fig.add_trace(trace, row=row, col=col)
            chart_idx += 1

        fig.update_layout(
            height=400 * rows,
            width=1200,
            title_text="ROI Analysis Dashboard",
            showlegend=False,
        )

        return fig

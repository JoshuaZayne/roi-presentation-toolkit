"""
ROI Presentation Toolkit - CLI Interface
========================================

Command-line interface for ROI modeling and presentation generation.

Usage:
    python main.py calculate --current-cost 1000000 --efficiency 0.30 --license 200000
    python main.py tco --years 5 --include-hidden
    python main.py sensitivity --variable efficiency --range 0.2
    python main.py export --format excel --output roi_report.xlsx
    python main.py visualize --chart waterfall
    python main.py narrative --audience cfo
"""

import click
import json
import sys
from pathlib import Path
from datetime import datetime

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent))

from models.roi_model import ROIModel
from models.tco_model import TCOModel
from models.sensitivity import SensitivityAnalyzer, MonteCarloSimulator
from outputs.excel_export import ExcelExporter
from outputs.visualization import ChartGenerator
from templates.narratives import NarrativeGenerator


# Store context data between commands
class Context:
    def __init__(self):
        self.roi_result = None
        self.tco_result = None
        self.sensitivity_results = None
        self.inputs = {}


pass_context = click.make_pass_decorator(Context, ensure=True)


@click.group()
@click.version_option(version="1.0.0")
@click.pass_context
def cli(ctx):
    """ROI Presentation Toolkit - Generate compelling ROI analyses for enterprise sales."""
    ctx.ensure_object(Context)


@cli.command()
@click.option('--current-cost', '-c', type=float, required=True, help='Current annual operational cost')
@click.option('--efficiency', '-e', type=float, required=True, help='Expected efficiency gain (0.0-1.0)')
@click.option('--implementation', '-i', type=float, default=None, help='One-time implementation cost')
@click.option('--license', '-l', 'annual_license', type=float, required=True, help='Annual license/subscription cost')
@click.option('--years', '-y', type=int, default=3, help='Analysis period in years')
@click.option('--scenario', '-s', type=click.Choice(['conservative', 'moderate', 'aggressive', 'all']),
              default='moderate', help='Scenario type')
@click.option('--industry', type=str, default=None, help='Industry for benchmark adjustments')
@click.option('--json-output', is_flag=True, help='Output results as JSON')
def calculate(current_cost: float, efficiency: float, implementation: float,
              annual_license: float, years: int, scenario: str, industry: str, json_output: bool):
    """Calculate ROI for a prospect."""
    model = ROIModel()

    industry_multiplier = 1.0
    if industry:
        multipliers = {"banking": 1.15, "insurance": 1.10, "asset_management": 1.20, "payments": 1.05}
        industry_multiplier = multipliers.get(industry.lower(), 1.0)

    if scenario == 'all':
        results = model.calculate_all_scenarios(
            current_annual_cost=current_cost,
            efficiency_gain=efficiency,
            annual_license=annual_license,
            implementation_cost=implementation,
            years=years,
            industry_multiplier=industry_multiplier
        )

        if json_output:
            output = {name: r.to_dict() for name, r in results.items()}
            click.echo(json.dumps(output, indent=2))
        else:
            click.echo(f"\n{'='*70}")
            click.echo("ROI ANALYSIS - ALL SCENARIOS")
            click.echo(f"{'='*70}\n")

            click.echo(f"{'Scenario':<15} {'ROI %':>10} {'Payback':>12} {'NPV':>15} {'Net Benefit':>15}")
            click.echo("-" * 70)

            for name, result in results.items():
                payback_str = f"{result.payback_months:.0f} mo" if result.payback_months < 120 else "N/A"
                click.echo(f"{name.title():<15} {result.roi_percent:>9.1f}% {payback_str:>12} "
                          f"${result.npv:>13,.0f} ${result.three_year_net_benefit:>13,.0f}")
    else:
        result = model.calculate(
            current_annual_cost=current_cost,
            efficiency_gain=efficiency,
            implementation_cost=implementation,
            annual_license=annual_license,
            years=years,
            scenario=scenario,
            industry_multiplier=industry_multiplier
        )

        if json_output:
            click.echo(json.dumps(result.to_dict(), indent=2))
        else:
            click.echo(f"\n{'='*60}")
            click.echo(f"ROI ANALYSIS - {scenario.upper()} SCENARIO")
            click.echo(f"{'='*60}\n")

            click.echo("INPUTS:")
            click.echo(f"  Current Annual Cost:    ${current_cost:>14,.0f}")
            click.echo(f"  Efficiency Gain:        {efficiency*100:>14.1f}%")
            click.echo(f"  Implementation Cost:    ${result.implementation_cost:>14,.0f}")
            click.echo(f"  Annual License:         ${annual_license:>14,.0f}")
            click.echo(f"  Analysis Period:        {years:>14} years")
            click.echo()

            click.echo("RESULTS:")
            click.echo(f"  Annual Savings:         ${result.annual_savings:>14,.0f}")
            click.echo(f"  Net Annual Benefit:     ${result.net_annual_benefit:>14,.0f}")
            click.echo(f"  Total Investment:       ${result.total_investment:>14,.0f}")
            click.echo(f"  {years}-Year Net Benefit:     ${result.three_year_net_benefit:>14,.0f}")
            click.echo(f"  {'-'*44}")
            click.echo(f"  ROI:                    {result.roi_percent:>14.1f}%")
            payback_str = f"{result.payback_months:.0f} months" if result.payback_months < 120 else "N/A"
            click.echo(f"  Payback Period:         {payback_str:>14}")
            click.echo(f"  NPV:                    ${result.npv:>14,.0f}")
            if result.irr:
                click.echo(f"  IRR:                    {result.irr*100:>14.1f}%")
            click.echo()

            # Generate talking points
            narrator = NarrativeGenerator()
            points = narrator.get_talking_points(result.to_dict())
            if points:
                click.echo("KEY TALKING POINTS:")
                for point in points:
                    click.echo(f"  * {point}")


@cli.command()
@click.option('--years', '-y', type=int, default=5, help='Analysis period in years')
@click.option('--current-ops', type=float, default=300000, help='Current annual operations cost')
@click.option('--current-maint', type=float, default=100000, help='Current annual maintenance cost')
@click.option('--current-labor', type=float, default=0, help='Current annual labor cost')
@click.option('--implementation', '-i', type=float, default=100000, help='Implementation cost')
@click.option('--license', '-l', 'annual_license', type=float, default=150000, help='Annual license cost')
@click.option('--support', type=float, default=0, help='Annual support cost')
@click.option('--include-hidden', is_flag=True, help='Include hidden costs in analysis')
@click.option('--json-output', is_flag=True, help='Output results as JSON')
def tco(years: int, current_ops: float, current_maint: float, current_labor: float,
        implementation: float, annual_license: float, support: float,
        include_hidden: bool, json_output: bool):
    """Calculate Total Cost of Ownership comparison."""
    model = TCOModel()

    result = model.compare(
        current_state={
            'annual_operations': current_ops,
            'annual_maintenance': current_maint,
            'annual_labor': current_labor,
        },
        future_state={
            'implementation': implementation,
            'annual_license': annual_license,
            'annual_support': support,
        },
        years=years,
        include_hidden=include_hidden
    )

    if json_output:
        click.echo(json.dumps(result.to_dict(), indent=2))
    else:
        click.echo(f"\n{'='*60}")
        click.echo(f"TCO COMPARISON - {years} YEAR ANALYSIS")
        click.echo(f"{'='*60}\n")

        click.echo("CURRENT STATE:")
        click.echo(f"  Annual Operations:      ${current_ops:>14,.0f}")
        click.echo(f"  Annual Maintenance:     ${current_maint:>14,.0f}")
        if current_labor > 0:
            click.echo(f"  Annual Labor:           ${current_labor:>14,.0f}")
        click.echo(f"  {years}-Year TCO:             ${result.current_state_tco:>14,.0f}")
        click.echo()

        click.echo("FUTURE STATE (with solution):")
        click.echo(f"  Implementation:         ${implementation:>14,.0f}")
        click.echo(f"  Annual License:         ${annual_license:>14,.0f}")
        if support > 0:
            click.echo(f"  Annual Support:         ${support:>14,.0f}")
        click.echo(f"  {years}-Year TCO:             ${result.future_state_tco:>14,.0f}")
        click.echo()

        click.echo("COMPARISON:")
        click.echo(f"  TCO Savings:            ${result.tco_savings:>14,.0f}")
        click.echo(f"  Savings Percent:        {result.savings_percent:>14.1f}%")

        if include_hidden and result.hidden_costs_identified:
            click.echo()
            click.echo("HIDDEN COSTS IDENTIFIED:")
            for category, amount in result.hidden_costs_identified.items():
                click.echo(f"  {category.replace('_', ' ').title()}: ${amount:,.0f}")


@cli.command()
@click.option('--variable', '-v', type=click.Choice(['efficiency_gain', 'annual_license', 'implementation_cost', 'current_annual_cost']),
              required=True, help='Variable to analyze')
@click.option('--range', '-r', 'range_pct', type=float, default=0.2, help='Variation range (e.g., 0.2 for +/-20%)')
@click.option('--current-cost', '-c', type=float, default=500000, help='Base current annual cost')
@click.option('--efficiency', '-e', type=float, default=0.30, help='Base efficiency gain')
@click.option('--license', '-l', 'annual_license', type=float, default=150000, help='Base annual license')
@click.option('--monte-carlo', is_flag=True, help='Run Monte Carlo simulation')
@click.option('--iterations', type=int, default=10000, help='Monte Carlo iterations')
@click.option('--json-output', is_flag=True, help='Output results as JSON')
def sensitivity(variable: str, range_pct: float, current_cost: float, efficiency: float,
                annual_license: float, monte_carlo: bool, iterations: int, json_output: bool):
    """Perform sensitivity analysis on ROI inputs."""

    base_inputs = {
        'current_annual_cost': current_cost,
        'efficiency_gain': efficiency,
        'annual_license': annual_license,
        'years': 3
    }

    if monte_carlo:
        simulator = MonteCarloSimulator()
        result = simulator.simulate(base_inputs, iterations=iterations)

        if json_output:
            click.echo(json.dumps(result.to_dict(), indent=2))
        else:
            click.echo(f"\n{'='*60}")
            click.echo(f"MONTE CARLO SIMULATION ({iterations:,} iterations)")
            click.echo(f"{'='*60}\n")

            click.echo("ROI DISTRIBUTION:")
            click.echo(f"  Mean ROI:               {result.roi_mean:>14.1f}%")
            click.echo(f"  Median ROI:             {result.roi_median:>14.1f}%")
            click.echo(f"  Std Deviation:          {result.roi_std:>14.1f}%")
            click.echo()
            click.echo("CONFIDENCE INTERVALS:")
            click.echo(f"  10th Percentile:        {result.roi_p10:>14.1f}%")
            click.echo(f"  50th Percentile:        {result.roi_p50:>14.1f}%")
            click.echo(f"  90th Percentile:        {result.roi_p90:>14.1f}%")
            click.echo()
            click.echo("PROBABILITIES:")
            click.echo(f"  Positive ROI:           {result.probability_positive_roi*100:>14.1f}%")
            click.echo(f"  ROI > 100%:             {result.probability_above_hurdle*100:>14.1f}%")
    else:
        analyzer = SensitivityAnalyzer()
        results = analyzer.tornado_analysis(base_inputs, range_pct=range_pct)

        if json_output:
            output = [r.to_dict() for r in results]
            click.echo(json.dumps(output, indent=2))
        else:
            click.echo(f"\n{'='*70}")
            click.echo(f"SENSITIVITY ANALYSIS - {variable.upper().replace('_', ' ')}")
            click.echo(f"{'='*70}\n")

            click.echo(f"{'Variable':<25} {'Low ROI':>12} {'Base ROI':>12} {'High ROI':>12} {'Impact':>10}")
            click.echo("-" * 70)

            for r in results:
                click.echo(f"{r.variable:<25} {r.low_roi:>11.1f}% {r.base_roi:>11.1f}% "
                          f"{r.high_roi:>11.1f}% {r.impact_range:>9.1f}%")


@cli.command()
@click.option('--format', '-f', 'fmt', type=click.Choice(['excel', 'html', 'json']),
              default='excel', help='Export format')
@click.option('--output', '-o', type=str, default=None, help='Output file path')
@click.option('--prospect', '-p', type=str, default='Prospect', help='Prospect/client name')
@click.option('--current-cost', '-c', type=float, default=1000000, help='Current annual cost')
@click.option('--efficiency', '-e', type=float, default=0.30, help='Efficiency gain')
@click.option('--license', '-l', 'annual_license', type=float, default=200000, help='Annual license')
def export(fmt: str, output: str, prospect: str, current_cost: float, efficiency: float, annual_license: float):
    """Export ROI analysis to file."""
    output_dir = Path(__file__).parent.parent / "output"
    output_dir.mkdir(exist_ok=True)

    # Generate data
    roi_model = ROIModel()
    tco_model = TCOModel()
    analyzer = SensitivityAnalyzer()

    roi_result = roi_model.calculate(
        current_annual_cost=current_cost,
        efficiency_gain=efficiency,
        annual_license=annual_license
    )

    tco_result = tco_model.compare(
        current_state={'annual_operations': current_cost * 0.6, 'annual_maintenance': current_cost * 0.4},
        future_state={'implementation': annual_license * 1.2, 'annual_license': annual_license},
        years=5
    )

    sensitivity_results = analyzer.tornado_analysis({
        'current_annual_cost': current_cost,
        'efficiency_gain': efficiency,
        'annual_license': annual_license,
        'years': 3
    })

    inputs = {
        'current_annual_cost': current_cost,
        'efficiency_gain': efficiency,
        'annual_license': annual_license,
        'years': 3
    }

    if output is None:
        ext = {'excel': 'xlsx', 'html': 'html', 'json': 'json'}[fmt]
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        output = str(output_dir / f"roi_analysis_{timestamp}.{ext}")

    if fmt == 'excel':
        exporter = ExcelExporter()
        path = exporter.generate_report(
            prospect_name=prospect,
            inputs=inputs,
            roi_result=roi_result,
            tco_result=tco_result,
            sensitivity_results=sensitivity_results,
            output_path=output
        )
    elif fmt == 'html':
        chart_gen = ChartGenerator()
        dashboard = chart_gen.create_dashboard(roi_result.to_dict(), tco_result.to_dict(), sensitivity_results)
        dashboard.write_html(output)
        path = output
    else:  # json
        data = {
            'prospect': prospect,
            'generated': datetime.now().isoformat(),
            'inputs': inputs,
            'roi_result': roi_result.to_dict(),
            'tco_result': tco_result.to_dict(),
            'sensitivity_results': [r.to_dict() for r in sensitivity_results]
        }
        with open(output, 'w') as f:
            json.dump(data, f, indent=2)
        path = output

    click.echo(f"\nExport saved to: {path}")


@cli.command()
@click.option('--chart', '-c', type=click.Choice(['waterfall', 'tco', 'payback', 'tornado', 'monte-carlo', 'dashboard']),
              required=True, help='Chart type to generate')
@click.option('--output', '-o', type=str, default=None, help='Output file path')
@click.option('--format', '-f', 'fmt', type=click.Choice(['html', 'png']), default='html', help='Output format')
@click.option('--current-cost', '-c', 'cost', type=float, default=1000000, help='Current annual cost')
@click.option('--efficiency', '-e', type=float, default=0.30, help='Efficiency gain')
@click.option('--license', '-l', 'annual_license', type=float, default=200000, help='Annual license')
def visualize(chart: str, output: str, fmt: str, cost: float, efficiency: float, annual_license: float):
    """Generate interactive visualizations."""
    output_dir = Path(__file__).parent.parent / "output"
    output_dir.mkdir(exist_ok=True)

    chart_gen = ChartGenerator()
    roi_model = ROIModel()
    tco_model = TCOModel()

    roi_result = roi_model.calculate(
        current_annual_cost=cost,
        efficiency_gain=efficiency,
        annual_license=annual_license
    )

    if output is None:
        output = str(output_dir / f"{chart}_chart.{fmt}")

    if chart == 'waterfall':
        fig = chart_gen.roi_waterfall(roi_result.to_dict())
    elif chart == 'tco':
        tco_result = tco_model.compare(
            current_state={'annual_operations': cost * 0.6, 'annual_maintenance': cost * 0.4},
            future_state={'implementation': annual_license * 1.2, 'annual_license': annual_license},
            years=5
        )
        fig = chart_gen.tco_comparison(tco_result.to_dict())
    elif chart == 'payback':
        fig = chart_gen.payback_timeline(roi_result.to_dict())
    elif chart == 'tornado':
        analyzer = SensitivityAnalyzer()
        results = analyzer.tornado_analysis({
            'current_annual_cost': cost,
            'efficiency_gain': efficiency,
            'annual_license': annual_license,
            'years': 3
        })
        fig = chart_gen.tornado_diagram(results)
    elif chart == 'monte-carlo':
        simulator = MonteCarloSimulator()
        mc_result = simulator.simulate({
            'current_annual_cost': cost,
            'efficiency_gain': efficiency,
            'annual_license': annual_license,
            'years': 3
        })
        fig = chart_gen.monte_carlo_distribution(mc_result)
    else:  # dashboard
        tco_result = tco_model.compare(
            current_state={'annual_operations': cost * 0.6, 'annual_maintenance': cost * 0.4},
            future_state={'implementation': annual_license * 1.2, 'annual_license': annual_license},
            years=5
        )
        analyzer = SensitivityAnalyzer()
        sensitivity_results = analyzer.tornado_analysis({
            'current_annual_cost': cost,
            'efficiency_gain': efficiency,
            'annual_license': annual_license,
            'years': 3
        })
        fig = chart_gen.create_dashboard(roi_result.to_dict(), tco_result.to_dict(), sensitivity_results)

    chart_gen.save_chart(fig, output, fmt)
    click.echo(f"\nChart saved to: {output}")


@cli.command()
@click.option('--audience', '-a', type=click.Choice(['cfo', 'cto', 'ceo', 'board', 'general']),
              default='general', help='Target executive audience')
@click.option('--prospect', '-p', type=str, default='Your Organization', help='Prospect/client name')
@click.option('--industry', type=str, default=None, help='Industry context')
@click.option('--current-cost', '-c', type=float, default=1000000, help='Current annual cost')
@click.option('--efficiency', '-e', type=float, default=0.30, help='Efficiency gain')
@click.option('--license', '-l', 'annual_license', type=float, default=200000, help='Annual license')
@click.option('--talking-points', is_flag=True, help='Output talking points only')
def narrative(audience: str, prospect: str, industry: str, current_cost: float,
              efficiency: float, annual_license: float, talking_points: bool):
    """Generate executive narrative and talking points."""
    model = ROIModel()
    result = model.calculate(
        current_annual_cost=current_cost,
        efficiency_gain=efficiency,
        annual_license=annual_license
    )

    generator = NarrativeGenerator(industry=industry or "general")

    if talking_points:
        points = generator.get_talking_points(result.to_dict())
        click.echo(f"\n{'='*60}")
        click.echo("KEY TALKING POINTS")
        click.echo(f"{'='*60}\n")
        for i, point in enumerate(points, 1):
            click.echo(f"  {i}. {point}")
    else:
        narrative_text = generator.generate(
            result.to_dict(),
            audience=audience,
            prospect_name=prospect
        )
        click.echo(narrative_text)


if __name__ == '__main__':
    cli()

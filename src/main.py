"""
ROI Presentation Toolkit - CLI Interface
========================================

Command-line interface for ROI modeling and presentation generation.
"""

import click
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from models.roi_model import ROIModel
from models.tco_model import TCOModel
from models.sensitivity import SensitivityAnalysis
from outputs.excel_export import ExcelExporter
from outputs.visualization import ChartGenerator
from templates.narratives import NarrativeGenerator


@click.group()
@click.version_option(version="1.0.0")
def cli():
    """ROI Presentation Toolkit - Generate compelling ROI analyses for enterprise sales."""
    pass


@cli.command()
@click.option('--current-cost', '-c', type=float, required=True, help='Current annual cost')
@click.option('--efficiency', '-e', type=float, required=True, help='Efficiency gain (0.0-1.0)')
@click.option('--implementation', '-i', type=float, default=0, help='Implementation cost')
@click.option('--license', '-l', 'annual_license', type=float, default=0, help='Annual license cost')
@click.option('--years', '-y', type=int, default=3, help='Analysis period')
@click.option('--scenario', type=click.Choice(['conservative', 'moderate', 'aggressive']),
              default='moderate', help='Scenario')
def calculate(current_cost: float, efficiency: float, implementation: float,
              annual_license: float, years: int, scenario: str):
    """Calculate ROI for a prospect."""
    model = ROIModel()

    result = model.calculate(
        current_annual_cost=current_cost,
        efficiency_gain=efficiency,
        implementation_cost=implementation,
        annual_license=annual_license,
        years=years,
        scenario=scenario
    )

    click.echo(f"\n{'='*60}")
    click.echo(f"ROI ANALYSIS - {scenario.upper()} SCENARIO")
    click.echo(f"{'='*60}\n")

    click.echo("INPUTS:")
    click.echo(f"  Current Annual Cost:    ${current_cost:>12,.2f}")
    click.echo(f"  Efficiency Gain:        {efficiency*100:>12.1f}%")
    click.echo(f"  Implementation Cost:    ${implementation:>12,.2f}")
    click.echo(f"  Annual License:         ${annual_license:>12,.2f}")
    click.echo()

    click.echo("RESULTS:")
    click.echo(f"  Annual Savings:         ${result['annual_savings']:>12,.2f}")
    click.echo(f"  Net Annual Benefit:     ${result['net_annual_benefit']:>12,.2f}")
    click.echo(f"  Total Investment:       ${result['total_investment']:>12,.2f}")
    click.echo(f"  {years}-Year Net Benefit:     ${result['total_net_benefit']:>12,.2f}")
    click.echo(f"  {'-'*40}")
    click.echo(f"  ROI:                    {result['roi_percent']:>12.1f}%")
    click.echo(f"  Payback Period:         {result['payback_months']:>12.1f} months")
    click.echo(f"  NPV (@10%):             ${result.get('npv', 0):>12,.2f}")
    click.echo()

    click.echo("TALKING POINTS:")
    for point in result.get('talking_points', []):
        click.echo(f"  - {point}")


@cli.command()
@click.option('--years', '-y', type=int, default=5, help='Analysis period')
@click.option('--current-ops', type=float, default=300000, help='Current operations cost')
@click.option('--current-maint', type=float, default=100000, help='Current maintenance cost')
@click.option('--implementation', '-i', type=float, default=100000, help='Implementation cost')
@click.option('--license', '-l', 'annual_license', type=float, default=150000, help='Annual license')
@click.option('--include-hidden', is_flag=True, help='Include hidden costs')
def tco(years: int, current_ops: float, current_maint: float, implementation: float,
        annual_license: float, include_hidden: bool):
    """Calculate Total Cost of Ownership comparison."""
    model = TCOModel()

    result = model.compare(
        current_state={
            'annual_operations': current_ops,
            'annual_maintenance': current_maint
        },
        future_state={
            'implementation': implementation,
            'annual_license': annual_license
        },
        years=years,
        include_hidden=include_hidden
    )

    click.echo(f"\n{'='*60}")
    click.echo(f"TCO COMPARISON - {years} YEAR ANALYSIS")
    click.echo(f"{'='*60}\n")

    click.echo("CURRENT STATE:")
    click.echo(f"  Annual Operations:      ${current_ops:>12,.2f}")
    click.echo(f"  Annual Maintenance:     ${current_maint:>12,.2f}")
    if include_hidden:
        click.echo(f"  Hidden Costs (est):     ${result.get('current_hidden', 0):>12,.2f}")
    click.echo(f"  {years}-Year TCO:             ${result['current_tco']:>12,.2f}")
    click.echo()

    click.echo("FUTURE STATE (with solution):")
    click.echo(f"  Implementation:         ${implementation:>12,.2f}")
    click.echo(f"  Annual License:         ${annual_license:>12,.2f}")
    click.echo(f"  {years}-Year TCO:             ${result['future_tco']:>12,.2f}")
    click.echo()

    click.echo("COMPARISON:")
    click.echo(f"  TCO Savings:            ${result['tco_savings']:>12,.2f}")
    click.echo(f"  Savings Percent:        {result['savings_percent']:>12.1f}%")


@cli.command()
@click.option('--variable', '-v', type=click.Choice(['efficiency', 'license', 'implementation']),
              required=True, help='Variable to analyze')
@click.option('--range', '-r', 'range_pct', type=float, default=0.2, help='Variation range')
def sensitivity(variable: str, range_pct: float):
    """Perform sensitivity analysis."""
    analysis = SensitivityAnalysis()

    base_inputs = {
        'current_annual_cost': 500000,
        'efficiency_gain': 0.30,
        'implementation_cost': 100000,
        'annual_license': 150000,
        'years': 3
    }

    results = analysis.one_way(base_inputs, variable, range_pct)
    click.echo(f"\n{'='*60}")
    click.echo(f"SENSITIVITY ANALYSIS - {variable.upper()}")
    click.echo(f"{'='*60}\n")

    click.echo(f"{'Scenario':<20} {'Value':>15} {'ROI':>12} {'Payback':>12}")
    click.echo("-" * 60)

    for r in results:
        click.echo(f"{r['label']:<20} {r['value']:>15,.2f} {r['roi']:>11.1f}% {r['payback']:>10.1f}mo")


@cli.command()
@click.option('--format', '-f', 'fmt', type=click.Choice(['excel', 'html']),
              default='excel', help='Export format')
@click.option('--output', '-o', type=str, default=None, help='Output file path')
@click.option('--prospect', '-p', type=str, default='Prospect', help='Prospect name')
def export(fmt: str, output: str, prospect: str):
    """Export ROI analysis to file."""
    output_dir = Path(__file__).parent.parent / "output"
    output_dir.mkdir(exist_ok=True)

    if output is None:
        ext = 'xlsx' if fmt == 'excel' else 'html'
        output = str(output_dir / f"roi_analysis.{ext}")

    if fmt == 'excel':
        exporter = ExcelExporter()
        path = exporter.generate_report(prospect_name=prospect, output_path=output)
    else:
        chart_gen = ChartGenerator()
        model = ROIModel()
        result = model.calculate(
            current_annual_cost=500000, efficiency_gain=0.30,
            implementation_cost=100000, annual_license=150000
        )
        fig = chart_gen.roi_waterfall(result)
        fig.write_html(output)
        path = output

    click.echo(f"\nExport saved to: {path}")


@cli.command()
@click.option('--audience', '-a', type=click.Choice(['cfo', 'cto', 'ceo', 'general']),
              default='general', help='Target audience')
def narrative(audience: str):
    """Generate executive narrative."""
    generator = NarrativeGenerator()
    model = ROIModel()

    result = model.calculate(
        current_annual_cost=500000, efficiency_gain=0.30,
        implementation_cost=100000, annual_license=150000
    )

    narrative_text = generator.generate(result, audience=audience)

    click.echo(f"\n{'='*60}")
    click.echo(f"EXECUTIVE NARRATIVE - {audience.upper()}")
    click.echo(f"{'='*60}\n")
    click.echo(narrative_text)


if __name__ == '__main__':
    cli()

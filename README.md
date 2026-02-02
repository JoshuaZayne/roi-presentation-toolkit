# Client ROI Presentation Toolkit

A comprehensive Python-based ROI modeling and presentation generation toolkit designed for C-level audiences in enterprise software and fintech sales.

## Overview

This toolkit provides comprehensive ROI analysis capabilities including:
- **ROI Calculations**: Multi-scenario (conservative, moderate, aggressive) return on investment analysis
- **TCO Modeling**: 5-year Total Cost of Ownership projections with hidden cost analysis
- **Sensitivity Analysis**: Monte Carlo simulation and break-even analysis
- **Professional Exports**: Excel workbooks with charts and conditional formatting
- **Interactive Visualizations**: Plotly-based charts (waterfall, tornado, comparison)
- **Executive Narratives**: C-level ready talking points and summaries

## Installation

```bash
pip install -r requirements.txt
```

## Quick Start

### Basic ROI Calculation
```bash
python src/main.py calculate --current-cost 1000000 --efficiency 0.30 --license 200000
```

### All Scenarios Analysis
```bash
python src/main.py calculate --current-cost 1000000 --efficiency 0.30 --license 200000 --scenario all
```

### TCO Analysis
```bash
python src/main.py tco --years 5 --include-hidden
```

### Sensitivity Analysis
```bash
python src/main.py sensitivity --variable efficiency_gain --range 0.2
```

### Monte Carlo Simulation
```bash
python src/main.py sensitivity --variable efficiency_gain --monte-carlo --iterations 10000
```

### Export to Excel
```bash
python src/main.py export --format excel --output roi_report.xlsx --prospect "Acme Corp"
```

### Generate Visualizations
```bash
python src/main.py visualize --chart waterfall
python src/main.py visualize --chart tornado
python src/main.py visualize --chart dashboard
```

### Executive Narrative
```bash
python src/main.py narrative --audience cfo --prospect "Acme Corp"
```

## Project Structure

```
roi-presentation-toolkit/
├── config/
│   ├── config.json              # Application configuration
│   └── assumptions.json         # Default ROI assumptions
├── src/
│   ├── main.py                  # CLI entry point
│   ├── models/
│   │   ├── roi_model.py         # Core ROI calculations
│   │   ├── tco_model.py         # Total Cost of Ownership
│   │   └── sensitivity.py       # Sensitivity analysis
│   ├── inputs/
│   │   └── client_data.py       # Client input handling
│   ├── outputs/
│   │   ├── excel_export.py      # Excel workbook generation
│   │   └── visualization.py     # Plotly charts
│   └── templates/
│       └── narratives.py        # Value proposition templates
├── data/
│   └── industry_benchmarks.json # Industry benchmark data
├── docs/
│   └── ROI_METHODOLOGY.md       # Methodology documentation
└── output/                      # Generated reports
```

## Key Metrics Calculated

| Metric | Description |
|--------|-------------|
| Annual Savings | Current costs x Efficiency gain percentage |
| Net Annual Benefit | Annual savings - Annual license cost |
| 3-Year ROI % | (3-year net benefit / Total investment) x 100 |
| Payback Period | Months until investment is recovered |
| NPV | Net Present Value using configurable discount rate |
| IRR | Internal Rate of Return |

## Requirements

- Python 3.8+
- openpyxl, pandas, numpy, plotly, click, scipy

## License

Proprietary - Internal Use Only

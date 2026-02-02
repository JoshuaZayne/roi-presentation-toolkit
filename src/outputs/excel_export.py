"""Excel Export Module"""
from pathlib import Path
from typing import Dict, Any, Optional
from datetime import datetime

try:
    from openpyxl import Workbook
    from openpyxl.styles import Font, PatternFill, Alignment
    OPENPYXL_AVAILABLE = True
except ImportError:
    OPENPYXL_AVAILABLE = False

class ExcelExporter:
    def __init__(self):
        if not OPENPYXL_AVAILABLE:
            raise ImportError("openpyxl required. Install: pip install openpyxl")
        self.header_font = Font(bold=True, size=12, color="FFFFFF")
        self.header_fill = PatternFill(start_color="1F4E79", fill_type="solid")

    def generate_report(self, prospect_name: str = "Prospect",
                        inputs: Optional[Dict] = None,
                        results: Optional[Dict] = None,
                        output_path: str = "roi_report.xlsx") -> str:
        wb = Workbook()

        # Executive Summary
        ws = wb.active
        ws.title = "Executive Summary"
        ws['A1'] = f"ROI Analysis: {prospect_name}"
        ws['A1'].font = Font(bold=True, size=14)
        ws['A2'] = f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M')}"

        ws['A4'] = "KEY METRICS"
        ws['A4'].font = self.header_font
        ws['A4'].fill = self.header_fill

        metrics = [
            ("Annual Savings", "$__________"),
            ("3-Year ROI", "__________ %"),
            ("Payback Period", "__________ months"),
            ("NPV (@10%)", "$__________"),
            ("Total Net Benefit", "$__________")
        ]
        for i, (label, value) in enumerate(metrics, 5):
            ws[f'A{i}'] = label
            ws[f'B{i}'] = value

        ws.column_dimensions['A'].width = 25
        ws.column_dimensions['B'].width = 20

        # Assumptions Sheet
        ws2 = wb.create_sheet("Assumptions")
        ws2['A1'] = "INPUT ASSUMPTIONS"
        ws2['A1'].font = Font(bold=True)

        assumptions = [
            ("Current Annual Cost", "$__________"),
            ("Efficiency Gain", "__________ %"),
            ("Implementation Cost", "$__________"),
            ("Annual License", "$__________"),
            ("Analysis Period", "__________ years")
        ]
        for i, (label, value) in enumerate(assumptions, 2):
            ws2[f'A{i}'] = label
            ws2[f'B{i}'] = value

        wb.save(output_path)
        return output_path

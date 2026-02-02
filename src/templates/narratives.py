"""Narrative Templates for Executive Presentations"""
from typing import Dict, Any

class NarrativeGenerator:
    """Generate executive-ready narratives for ROI presentations."""

    def generate(self, result: Dict[str, Any], audience: str = "general") -> str:
        roi = result.get('roi_percent', 0)
        payback = result.get('payback_months', 0)
        savings = result.get('annual_savings', 0)
        net_benefit = result.get('total_net_benefit', 0)

        if audience == "cfo":
            return self._cfo_narrative(roi, payback, savings, net_benefit)
        elif audience == "cto":
            return self._cto_narrative(roi, payback, savings, net_benefit)
        elif audience == "ceo":
            return self._ceo_narrative(roi, payback, savings, net_benefit)
        else:
            return self._general_narrative(roi, payback, savings, net_benefit)

    def _cfo_narrative(self, roi, payback, savings, net_benefit) -> str:
        return f"""EXECUTIVE SUMMARY FOR CFO

Financial Impact:
This investment delivers a {roi:.0f}% return over three years, with the initial
investment recovered in {payback:.0f} months. The projected annual savings of
${savings:,.0f} will contribute ${net_benefit:,.0f} in cumulative net benefit.

Risk-Adjusted Analysis:
Even under conservative assumptions (70% of projected efficiency gains), the ROI
remains strongly positive. The payback period falls well within acceptable capital
allocation guidelines.

Recommendation:
Proceed with implementation. The financial returns justify the investment, and the
operational efficiency gains align with cost optimization initiatives."""

    def _cto_narrative(self, roi, payback, savings, net_benefit) -> str:
        return f"""EXECUTIVE SUMMARY FOR CTO

Technical Value:
This solution modernizes our data infrastructure while delivering {roi:.0f}% ROI.
The implementation will reduce technical debt and enable faster innovation cycles.

Integration Benefits:
- Pre-built connectors minimize IT resource requirements
- Cloud-native architecture reduces maintenance overhead
- API-first design enables future extensibility

Recommendation:
The technical capabilities align with our digital transformation roadmap. The
{payback:.0f}-month payback period makes this a financially sound technology investment."""

    def _ceo_narrative(self, roi, payback, savings, net_benefit) -> str:
        return f"""EXECUTIVE SUMMARY FOR CEO

Strategic Impact:
This initiative delivers {roi:.0f}% ROI while advancing our competitive positioning
in the market. The ${savings:,.0f} in annual savings can be reinvested in growth
initiatives.

Competitive Advantage:
- Enhanced member/customer experience capabilities
- Data-driven decision making across the organization
- Foundation for future AI/ML initiatives

Recommendation:
Approve this investment. The combination of strong financial returns and strategic
capabilities makes this a priority initiative."""

    def _general_narrative(self, roi, payback, savings, net_benefit) -> str:
        return f"""EXECUTIVE SUMMARY

Investment Overview:
This solution delivers a compelling {roi:.0f}% return on investment over three years.
With annual savings of ${savings:,.0f} and a payback period of {payback:.0f} months,
the financial case is strong.

Key Highlights:
- Total 3-year net benefit: ${net_benefit:,.0f}
- Payback period: {payback:.0f} months
- Risk-adjusted returns remain positive under conservative scenarios

Next Steps:
We recommend proceeding to contract negotiation to capture these benefits."""

    def get_talking_points(self, result: Dict[str, Any]) -> List[str]:
        roi = result.get('roi_percent', 0)
        payback = result.get('payback_months', 0)
        savings = result.get('annual_savings', 0)

        points = []
        if roi > 0:
            points.append(f"{roi:.0f}% 3-year ROI")
        if payback < 24:
            points.append(f"{payback:.0f}-month payback period")
        if savings > 0:
            points.append(f"${savings:,.0f} annual savings")
        if roi > 300:
            points.append("Exceeds industry ROI benchmarks")
        return points

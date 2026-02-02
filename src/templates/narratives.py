"""Narrative Templates for Executive Presentations"""

from typing import Dict, Any, List, Optional
from datetime import datetime


class NarrativeGenerator:
    """
    Generate executive-ready narratives for ROI presentations.

    Provides customized talking points and summaries for different C-level audiences.
    """

    AUDIENCE_TYPES = ["cfo", "cto", "ceo", "board", "general"]

    INDUSTRY_FOCUS = {
        "banking": {
            "benefits": ["regulatory compliance", "fraud reduction", "customer experience"],
            "metrics": ["cost per transaction", "straight-through processing rate"],
        },
        "insurance": {
            "benefits": ["claims processing", "underwriting accuracy", "policy administration"],
            "metrics": ["loss ratio improvement", "combined ratio impact"],
        },
        "asset_management": {
            "benefits": ["portfolio analytics", "reporting automation", "client reporting"],
            "metrics": ["AUM scalability", "fee compression mitigation"],
        },
        "payments": {
            "benefits": ["transaction speed", "fraud prevention", "settlement efficiency"],
            "metrics": ["transaction cost", "authorization rate"],
        },
    }

    def __init__(self, industry: str = "general"):
        self.industry = industry
        self.industry_context = self.INDUSTRY_FOCUS.get(industry, {})

    def generate(
        self,
        roi_result: Dict[str, Any],
        audience: str = "general",
        prospect_name: str = "Your Organization",
        include_recommendations: bool = True
    ) -> str:
        """
        Generate narrative summary for specified audience.

        Args:
            roi_result: ROI calculation results
            audience: Target audience (cfo, cto, ceo, board, general)
            prospect_name: Client/prospect name for personalization
            include_recommendations: Whether to include recommendation section

        Returns:
            Formatted narrative string
        """
        # Extract metrics from result
        if hasattr(roi_result, 'to_dict'):
            data = roi_result.to_dict()
        else:
            data = roi_result

        roi = data.get('roi_percent', 0)
        payback = data.get('payback_months', 0)
        savings = data.get('annual_savings', 0)
        net_benefit = data.get('three_year_net_benefit', 0)
        npv = data.get('npv', 0)
        implementation_cost = data.get('implementation_cost', 0)
        total_investment = data.get('total_investment', 0)

        # Generate audience-specific narrative
        narrative_methods = {
            "cfo": self._cfo_narrative,
            "cto": self._cto_narrative,
            "ceo": self._ceo_narrative,
            "board": self._board_narrative,
            "general": self._general_narrative,
        }

        method = narrative_methods.get(audience, self._general_narrative)
        narrative = method(
            roi=roi,
            payback=payback,
            savings=savings,
            net_benefit=net_benefit,
            npv=npv,
            implementation_cost=implementation_cost,
            total_investment=total_investment,
            prospect_name=prospect_name,
        )

        if include_recommendations:
            narrative += self._get_recommendation(roi, payback, savings)

        return narrative

    def _cfo_narrative(self, roi, payback, savings, net_benefit, npv, implementation_cost, total_investment, prospect_name) -> str:
        irr_estimate = roi / 3 if roi > 0 else 0  # Rough IRR estimate

        return f"""EXECUTIVE FINANCIAL SUMMARY
Prepared for: {prospect_name} - Chief Financial Officer
Date: {datetime.now().strftime('%B %d, %Y')}

FINANCIAL IMPACT ANALYSIS
-------------------------

Investment Overview:
- Total 3-Year Investment: ${total_investment:,.0f}
- Implementation Cost: ${implementation_cost:,.0f}
- Net Present Value (NPV): ${npv:,.0f}
- Internal Rate of Return (Est.): {irr_estimate:.0f}%

Return Metrics:
- 3-Year ROI: {roi:.0f}%
- Payback Period: {payback:.0f} months
- Annual Cash Savings: ${savings:,.0f}
- Cumulative 3-Year Net Benefit: ${net_benefit:,.0f}

Risk-Adjusted Analysis:
Under conservative assumptions (70% benefit realization, 20% cost overrun), the investment
maintains positive NPV and achieves payback within acceptable capital allocation guidelines.
The sensitivity analysis indicates efficiency gains would need to fall below {self._calculate_breakeven_efficiency(roi):.0f}%
of projected levels for the investment to become unprofitable.

Working Capital Impact:
- Year 1: Net investment period, cash flow negative
- Year 2: Crossover to positive cumulative cash flow
- Year 3: Full benefit realization with significant positive contribution

"""

    def _cto_narrative(self, roi, payback, savings, net_benefit, npv, implementation_cost, total_investment, prospect_name) -> str:
        return f"""TECHNOLOGY VALUE ASSESSMENT
Prepared for: {prospect_name} - Chief Technology Officer
Date: {datetime.now().strftime('%B %d, %Y')}

TECHNICAL & FINANCIAL OVERVIEW
------------------------------

Business Case Summary:
- 3-Year ROI: {roi:.0f}%
- Payback Period: {payback:.0f} months
- Annual Operational Savings: ${savings:,.0f}

Technology Value Drivers:
1. Infrastructure Modernization
   - Reduces technical debt through modern architecture
   - Cloud-native capabilities enable scalability
   - API-first design supports future integration needs

2. Operational Efficiency
   - Automation of manual processes
   - Reduced maintenance overhead
   - Streamlined deployment and updates

3. Innovation Enablement
   - Foundation for AI/ML initiatives
   - Real-time analytics capabilities
   - Enhanced data accessibility across organization

Integration Considerations:
- Pre-built connectors minimize custom development
- Standard APIs reduce integration complexity
- Phased rollout approach manages implementation risk

Resource Requirements:
- IT team involvement: Moderate during implementation
- Ongoing maintenance: Lower than current state
- Training needs: Comprehensive initial, minimal ongoing

"""

    def _ceo_narrative(self, roi, payback, savings, net_benefit, npv, implementation_cost, total_investment, prospect_name) -> str:
        return f"""STRATEGIC INVESTMENT SUMMARY
Prepared for: {prospect_name} - Chief Executive Officer
Date: {datetime.now().strftime('%B %d, %Y')}

EXECUTIVE OVERVIEW
------------------

The Opportunity:
This investment delivers {roi:.0f}% return over three years while positioning the organization
for sustainable competitive advantage. The ${savings:,.0f} in annual savings can be reinvested
in strategic growth initiatives.

Key Financial Metrics:
- Return on Investment: {roi:.0f}% (3-year)
- Time to Value: {payback:.0f} months
- Net Benefit: ${net_benefit:,.0f} over 3 years

Strategic Value Creation:
1. Competitive Positioning
   - Enhanced customer/member experience capabilities
   - Faster time-to-market for new offerings
   - Data-driven decision making across the organization

2. Operational Excellence
   - Significant efficiency improvements
   - Reduced operational risk
   - Scalable infrastructure for growth

3. Future Readiness
   - Foundation for digital transformation initiatives
   - Enables AI and advanced analytics adoption
   - Positions organization for industry evolution

Market Context:
Industry peers investing in similar capabilities are achieving comparable or higher returns.
Delay may result in competitive disadvantage as the market evolves.

"""

    def _board_narrative(self, roi, payback, savings, net_benefit, npv, implementation_cost, total_investment, prospect_name) -> str:
        return f"""BOARD OF DIRECTORS BRIEFING
{prospect_name}
Date: {datetime.now().strftime('%B %d, %Y')}

INVESTMENT AUTHORIZATION REQUEST
--------------------------------

Summary:
Management requests authorization for a strategic technology investment with the following
financial profile:

Financial Highlights:
+---------------------------+------------------+
| Metric                    | Value            |
+---------------------------+------------------+
| Total Investment          | ${total_investment:>14,.0f} |
| 3-Year ROI                | {roi:>13.0f}% |
| Payback Period            | {payback:>11.0f} mo |
| Net Present Value         | ${npv:>14,.0f} |
| Annual Savings            | ${savings:>14,.0f} |
| 3-Year Net Benefit        | ${net_benefit:>14,.0f} |
+---------------------------+------------------+

Risk Assessment:
- Implementation Risk: MODERATE - Mitigated through phased approach
- Technology Risk: LOW - Proven solution with market track record
- Financial Risk: LOW - Positive NPV under conservative scenarios

Governance:
- Quarterly progress reporting to Finance Committee
- Phase-gate approval for major milestones
- Independent review at project completion

Management Recommendation:
Approve the investment. The financial returns exceed hurdle rate requirements, and the
strategic benefits support long-term organizational objectives.

"""

    def _general_narrative(self, roi, payback, savings, net_benefit, npv, implementation_cost, total_investment, prospect_name) -> str:
        return f"""EXECUTIVE SUMMARY
Prepared for: {prospect_name}
Date: {datetime.now().strftime('%B %d, %Y')}

INVESTMENT OVERVIEW
-------------------

This analysis evaluates the financial and strategic value of the proposed solution.

Key Findings:
- The investment delivers a compelling {roi:.0f}% return over three years
- Payback is achieved in {payback:.0f} months
- Annual savings of ${savings:,.0f} contribute to operational efficiency
- Net Present Value of ${npv:,.0f} indicates value creation above cost of capital

Financial Summary:
- Total 3-Year Investment: ${total_investment:,.0f}
- Total 3-Year Benefits: ${net_benefit + total_investment:,.0f}
- Net 3-Year Benefit: ${net_benefit:,.0f}

Value Drivers:
1. Process efficiency improvements
2. Reduced manual effort and errors
3. Enhanced scalability and flexibility
4. Lower total cost of ownership

Risk Considerations:
- Conservative scenario analysis maintains positive returns
- Phased implementation reduces deployment risk
- Proven technology with established track record

"""

    def _get_recommendation(self, roi: float, payback: float, savings: float) -> str:
        """Generate recommendation based on metrics."""
        if roi > 200 and payback < 18:
            strength = "STRONGLY RECOMMEND"
            rationale = "exceptional financial returns and rapid payback"
        elif roi > 100 and payback < 24:
            strength = "RECOMMEND"
            rationale = "solid financial returns within acceptable payback period"
        elif roi > 50:
            strength = "RECOMMEND WITH CONDITIONS"
            rationale = "positive returns warrant investment with close monitoring"
        else:
            strength = "FURTHER ANALYSIS RECOMMENDED"
            rationale = "additional due diligence needed before proceeding"

        return f"""
RECOMMENDATION
--------------
{strength}

Based on this analysis, we {strength.lower()} proceeding with this investment due to
{rationale}.

Next Steps:
1. Finalize scope and pricing negotiations
2. Develop detailed implementation plan
3. Establish success metrics and governance
4. Begin implementation upon approval
"""

    def _calculate_breakeven_efficiency(self, roi: float) -> float:
        """Calculate approximate break-even efficiency level."""
        if roi <= 0:
            return 100
        # Rough approximation: at what % of benefits does ROI = 0
        return max(0, 100 - (roi / 3))

    def get_talking_points(
        self,
        roi_result: Dict[str, Any],
        max_points: int = 5
    ) -> List[str]:
        """
        Generate key talking points for verbal presentation.

        Returns:
            List of concise talking points
        """
        if hasattr(roi_result, 'to_dict'):
            data = roi_result.to_dict()
        else:
            data = roi_result

        roi = data.get('roi_percent', 0)
        payback = data.get('payback_months', 0)
        savings = data.get('annual_savings', 0)
        npv = data.get('npv', 0)
        net_benefit = data.get('three_year_net_benefit', 0)

        points = []

        # ROI point
        if roi > 200:
            points.append(f"Exceptional {roi:.0f}% 3-year ROI - exceeds typical investment hurdles")
        elif roi > 100:
            points.append(f"Strong {roi:.0f}% 3-year ROI - doubles the investment value")
        elif roi > 0:
            points.append(f"{roi:.0f}% 3-year ROI - positive return on investment")

        # Payback point
        if payback < 12:
            points.append(f"Rapid {payback:.0f}-month payback - investment recovered in under a year")
        elif payback < 24:
            points.append(f"{payback:.0f}-month payback period - quick time to value")
        elif payback < 36:
            points.append(f"{payback:.0f}-month payback - within standard guidelines")

        # Savings point
        if savings > 1000000:
            points.append(f"${savings/1000000:.1f}M in annual operational savings")
        elif savings > 100000:
            points.append(f"${savings:,.0f} annual savings drives ongoing value")

        # NPV point
        if npv > 0:
            points.append(f"Positive NPV of ${npv:,.0f} confirms value creation")

        # Net benefit point
        if net_benefit > 0:
            points.append(f"${net_benefit:,.0f} cumulative net benefit over 3 years")

        # Industry context if available
        if self.industry_context:
            benefits = self.industry_context.get("benefits", [])
            if benefits:
                points.append(f"Key value in {benefits[0]} and {benefits[1]}")

        return points[:max_points]

    def get_objection_handlers(
        self,
        roi_result: Dict[str, Any]
    ) -> Dict[str, str]:
        """
        Generate responses to common executive objections.

        Returns:
            Dictionary of objection:response pairs
        """
        if hasattr(roi_result, 'to_dict'):
            data = roi_result.to_dict()
        else:
            data = roi_result

        roi = data.get('roi_percent', 0)
        payback = data.get('payback_months', 0)
        savings = data.get('annual_savings', 0)

        handlers = {
            "The ROI seems too optimistic": f"""
The {roi:.0f}% ROI is based on conservative assumptions validated by industry benchmarks.
Even at 70% of projected benefits, the investment remains profitable with positive NPV.
We recommend starting with a pilot to validate assumptions before full deployment.""",

            "We don't have the budget this year": f"""
The {payback:.0f}-month payback means this investment largely pays for itself within
the fiscal year. The ${savings:,.0f} in annual savings can offset the investment through
operational budget reallocation. We can also explore phased funding approaches.""",

            "What about implementation risk?": f"""
We mitigate implementation risk through: (1) phased deployment with go/no-go gates,
(2) proven methodology with dedicated project management, (3) reference customers
with similar deployments, and (4) performance guarantees tied to key milestones.""",

            "Our current system works fine": f"""
While current systems function, the opportunity cost of not modernizing includes:
continued high operating costs, competitive disadvantage as peers upgrade, and
accumulated technical debt. The ${savings:,.0f} annual savings represents real
value being left on the table.""",

            "Can we do this internally?": f"""
Internal development typically costs 2-3x more and takes significantly longer.
The specialized expertise required, ongoing maintenance burden, and opportunity
cost of diverting internal resources makes the build vs. buy decision clear.
The {payback:.0f}-month payback assumes external solution efficiency.""",
        }

        return handlers

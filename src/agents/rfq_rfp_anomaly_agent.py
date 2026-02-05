"""
RFQ/RFP Anomaly Detection Agent - Detects anomalies in RFQs and RFPs.
Identifies irregularities, unusual patterns, pricing anomalies, and compliance issues.
"""
from typing import Dict, Any, List, Optional
from datetime import datetime
import json
import re
from src.utils.logging import get_logger
from src.models.core import AgentInput, AgentOutput
from src.core.llm_client import llm_client

logger = get_logger(__name__)


class RFQRFPAnomalyAgent:
    """
    RFQ/RFP Anomaly Detection Agent.
    Detects pricing anomalies, specification irregularities, and compliance issues.
    """
    
    name = "rfq_rfp_anomaly_agent"
    capabilities = [
        "pricing_anomaly_detection",
        "specification_validation",
        "compliance_checking",
        "bid_comparison",
        "outlier_identification",
        "pattern_detection",
        "completeness_verification"
    ]
    
    async def execute(self, agent_input: AgentInput) -> AgentOutput:
        """Execute RFQ/RFP anomaly detection."""
        start_time = datetime.utcnow()
        
        logger.info(
            "RFQ/RFP Anomaly agent executing",
            task_id=str(agent_input.task_id)
        )
        
        try:
            detection_type = agent_input.context.get("detection_type", "comprehensive")
            
            if detection_type == "pricing":
                result = await self._detect_pricing_anomalies(agent_input)
            elif detection_type == "specification":
                result = await self._validate_specifications(agent_input)
            elif detection_type == "compliance":
                result = await self._check_compliance(agent_input)
            elif detection_type == "bid_comparison":
                result = await self._compare_bids(agent_input)
            else:
                result = await self._comprehensive_anomaly_detection(agent_input)
            
            confidence = self._calculate_confidence(result)
            
            execution_time = (datetime.utcnow() - start_time).total_seconds() * 1000
            
            logger.info(
                "RFQ/RFP Anomaly agent completed",
                task_id=str(agent_input.task_id),
                anomalies_detected=len(result.get("anomalies", [])),
                confidence=confidence
            )
            
            return AgentOutput(
                task_id=agent_input.task_id,
                agent_name=self.name,
                result=result,
                confidence=confidence,
                execution_time_ms=execution_time,
                metadata={
                    "detection_type": detection_type,
                    "anomaly_count": len(result.get("anomalies", [])),
                    "critical_count": len([a for a in result.get("anomalies", []) if a.get("severity") == "Critical"])
                }
            )
            
        except Exception as e:
            logger.error(
                "RFQ/RFP Anomaly agent failed",
                task_id=str(agent_input.task_id),
                error=str(e)
            )
            
            execution_time = (datetime.utcnow() - start_time).total_seconds() * 1000
            
            return AgentOutput(
                task_id=agent_input.task_id,
                agent_name=self.name,
                result={},
                confidence=0.0,
                errors=[str(e)],
                execution_time_ms=execution_time
            )
    
    async def _detect_pricing_anomalies(self, agent_input: AgentInput) -> Dict[str, Any]:
        """Detect pricing anomalies in RFQ/RFP responses."""
        rfq_data = agent_input.context.get("rfq_data", {})
        bid_responses = agent_input.context.get("bid_responses", [])
        historical_data = agent_input.context.get("historical_data", {})
        
        memory_context_str = ""
        if agent_input.memory_context:
            memory_context_str = "\n\nHistorical Pricing Context:\n" + "\n".join(
                [f"- {item.get('content', {})}" for item in agent_input.memory_context[:3]]
            )
        
        prompt = f"""Analyze RFQ/RFP bids for pricing anomalies and irregularities.

RFQ Details:
{json.dumps(rfq_data, indent=2)[:1000]}

Bid Responses:
{json.dumps(bid_responses, indent=2)[:2000]}

Historical Pricing Data:
{json.dumps(historical_data, indent=2)[:1000]}
{memory_context_str}

Instructions: {agent_input.instructions}

Detect and analyze:
1. PRICING ANOMALIES
   - Unusually high or low bids
   - Outliers from market average
   - Suspicious pricing patterns
   - Missing cost breakdowns

2. STATISTICAL ANALYSIS
   - Calculate mean, median, standard deviation
   - Identify outliers (>2 standard deviations)
   - Price variance analysis
   - Bid clustering patterns

3. COMPARATIVE ANALYSIS
   - Compare with historical data
   - Industry benchmark comparison
   - Peer bid comparison
   - Regional pricing variation

4. RED FLAGS
   - Bids significantly below cost
   - Rounded numbers (possible estimation)
   - Identical bids from different vendors
   - Last-minute bid submissions
   - Missing itemization

5. RISK ASSESSMENT
   - Financial viability concerns
   - Potential loss leader bids
   - Collusion indicators
   - Scope misunderstanding

Output JSON format:
{{
    "anomalies": [
        {{
            "anomaly_id": "ANOM-001",
            "anomaly_type": "pricing_outlier",
            "vendor_name": "Vendor Name",
            "description": "Detailed description",
            "severity": "Critical/High/Medium/Low",
            "evidence": ["Evidence 1", "Evidence 2"],
            "statistical_basis": "2.5 std dev below mean",
            "impact": "Financial/Quality/Timeline",
            "recommendation": "Action to take",
            "confidence": 0.85
        }}
    ],
    "statistical_summary": {{
        "total_bids": 0,
        "mean_price": 0,
        "median_price": 0,
        "std_deviation": 0,
        "price_range": {{
            "min": 0,
            "max": 0
        }},
        "outliers": []
    }},
    "risk_assessment": {{
        "overall_risk": "High/Medium/Low",
        "risk_factors": [],
        "mitigation_steps": []
    }},
    "recommended_actions": [],
    "further_investigation_needed": []
}}

Analysis:"""

        response = await llm_client.generate(prompt, temperature=0.2)
        
        try:
            start_idx = response.find('{')
            end_idx = response.rfind('}') + 1
            
            if start_idx >= 0 and end_idx > start_idx:
                json_str = response[start_idx:end_idx]
                result = json.loads(json_str)
            else:
                result = self._create_fallback_pricing_analysis(response, bid_responses)
            
            # Add statistical analysis
            result = self._enhance_with_statistics(result, bid_responses)
            result["analysis_timestamp"] = datetime.utcnow().isoformat()
            
            return result
            
        except json.JSONDecodeError:
            return self._create_fallback_pricing_analysis(response, bid_responses)
    
    async def _validate_specifications(self, agent_input: AgentInput) -> Dict[str, Any]:
        """Validate RFQ/RFP specifications for completeness and clarity."""
        rfq_specifications = agent_input.context.get("specifications", "")
        requirements = agent_input.context.get("requirements", [])
        
        prompt = f"""Validate RFQ/RFP specifications for anomalies and issues.

Specifications:
{rfq_specifications[:2000]}

Requirements Checklist:
{json.dumps(requirements, indent=2)}

Instructions: {agent_input.instructions}

Analyze for:
1. COMPLETENESS
   - Missing critical specifications
   - Ambiguous requirements
   - Contradictory statements
   - Undefined terms

2. CLARITY
   - Vague descriptions
   - Measurability of requirements
   - Acceptance criteria clarity
   - Technical specification detail

3. COMPLIANCE
   - Regulatory requirements
   - Industry standards
   - Safety specifications
   - Quality standards

4. FEASIBILITY
   - Unrealistic timelines
   - Impossible specifications
   - Conflicting requirements
   - Resource constraints

5. CONSISTENCY
   - Internal contradictions
   - Version mismatches
   - Cross-reference errors

Output JSON:
{{
    "anomalies": [
        {{
            "anomaly_id": "SPEC-001",
            "category": "completeness/clarity/compliance/feasibility",
            "description": "Issue description",
            "severity": "Critical/High/Medium/Low",
            "location": "Section/Page reference",
            "impact": "Impact on bidding/execution",
            "recommendation": "How to fix"
        }}
    ],
    "completeness_score": 0.85,
    "clarity_score": 0.90,
    "overall_quality": "Excellent/Good/Fair/Poor",
    "missing_elements": [],
    "recommendations": []
}}

Validation:"""

        response = await llm_client.generate(prompt, temperature=0.2)
        
        try:
            start_idx = response.find('{')
            end_idx = response.rfind('}') + 1
            
            if start_idx >= 0 and end_idx > start_idx:
                json_str = response[start_idx:end_idx]
                return json.loads(json_str)
        except json.JSONDecodeError:
            pass
        
        return {
            "anomalies": [],
            "validation_text": response,
            "status": "manual_review_required"
        }
    
    async def _check_compliance(self, agent_input: AgentInput) -> Dict[str, Any]:
        """Check RFQ/RFP compliance with regulations and standards."""
        rfq_document = agent_input.context.get("rfq_document", "")
        compliance_requirements = agent_input.context.get("compliance_requirements", [])
        
        prompt = f"""Check RFQ/RFP for compliance issues and violations.

RFQ Document:
{rfq_document[:2000]}

Compliance Requirements:
{json.dumps(compliance_requirements, indent=2)}

Instructions: {agent_input.instructions}

Check for:
1. REGULATORY COMPLIANCE
   - Procurement regulations
   - Industry-specific regulations
   - Environmental compliance
   - Labor laws

2. STANDARD COMPLIANCE
   - ISO standards
   - Industry best practices
   - Quality standards
   - Safety standards

3. ORGANIZATIONAL POLICIES
   - Internal procurement policies
   - Approval requirements
   - Documentation standards
   - Vendor qualification criteria

4. LEGAL REQUIREMENTS
   - Contract law compliance
   - Fair competition
   - Non-discrimination
   - Data protection

Output JSON:
{{
    "compliance_status": "Compliant/Non-Compliant/Needs Review",
    "violations": [
        {{
            "violation_id": "COMP-001",
            "regulation": "Regulation name",
            "description": "Violation description",
            "severity": "Critical/High/Medium/Low",
            "remediation": "How to fix",
            "timeline": "When to fix by"
        }}
    ],
    "compliance_score": 0.85,
    "recommendations": []
}}

Compliance Check:"""

        response = await llm_client.generate(prompt, temperature=0.2)
        
        try:
            start_idx = response.find('{')
            end_idx = response.rfind('}') + 1
            
            if start_idx >= 0 and end_idx > start_idx:
                json_str = response[start_idx:end_idx]
                return json.loads(json_str)
        except json.JSONDecodeError:
            pass
        
        return {
            "compliance_status": "Needs Review",
            "analysis": response
        }
    
    async def _compare_bids(self, agent_input: AgentInput) -> Dict[str, Any]:
        """Compare multiple bids for anomalies and patterns."""
        bids = agent_input.context.get("bids", [])
        
        prompt = f"""Compare bids to identify anomalies and suspicious patterns.

Bids Data:
{json.dumps(bids, indent=2)[:3000]}

Instructions: {agent_input.instructions}

Analyze for:
1. SIMILARITY PATTERNS
   - Identical or very similar bids
   - Same pricing structures
   - Similar language/phrasing
   - Coordinated submission times

2. COLLUSION INDICATORS
   - Bid rotation patterns
   - Complementary bidding
   - Phantom bids
   - Market division

3. RESPONSIVENESS
   - Non-responsive bids
   - Incomplete submissions
   - Missing documentation
   - Late submissions

4. QUALIFICATION
   - Vendor qualifications mismatch
   - Experience discrepancies
   - Capacity concerns
   - Financial stability

Output JSON:
{{
    "comparison_summary": {{
        "total_bids": 0,
        "responsive_bids": 0,
        "qualified_bidders": 0
    }},
    "anomalies": [
        {{
            "anomaly_type": "Type",
            "vendors_involved": [],
            "description": "Description",
            "severity": "Level",
            "evidence": []
        }}
    ],
    "collusion_risk": "High/Medium/Low/None",
    "recommendations": []
}}

Comparison:"""

        response = await llm_client.generate(prompt, temperature=0.2)
        
        try:
            start_idx = response.find('{')
            end_idx = response.rfind('}') + 1
            
            if start_idx >= 0 and end_idx > start_idx:
                json_str = response[start_idx:end_idx]
                return json.loads(json_str)
        except json.JSONDecodeError:
            pass
        
        return {
            "comparison_summary": {"total_bids": len(bids)},
            "analysis": response
        }
    
    async def _comprehensive_anomaly_detection(self, agent_input: AgentInput) -> Dict[str, Any]:
        """Perform comprehensive anomaly detection across all dimensions."""
        # Combine all detection methods
        pricing_result = await self._detect_pricing_anomalies(agent_input)
        spec_result = await self._validate_specifications(agent_input)
        compliance_result = await self._check_compliance(agent_input)
        comparison_result = await self._compare_bids(agent_input)
        
        # Consolidate results
        all_anomalies = []
        all_anomalies.extend(pricing_result.get("anomalies", []))
        all_anomalies.extend(spec_result.get("anomalies", []))
        all_anomalies.extend(compliance_result.get("violations", []))
        all_anomalies.extend(comparison_result.get("anomalies", []))
        
        # Sort by severity
        severity_order = {"Critical": 0, "High": 1, "Medium": 2, "Low": 3}
        all_anomalies.sort(key=lambda x: severity_order.get(x.get("severity", "Low"), 4))
        
        return {
            "comprehensive_analysis": {
                "pricing_analysis": pricing_result,
                "specification_validation": spec_result,
                "compliance_check": compliance_result,
                "bid_comparison": comparison_result
            },
            "anomalies": all_anomalies,
            "total_anomalies": len(all_anomalies),
            "critical_issues": len([a for a in all_anomalies if a.get("severity") == "Critical"]),
            "overall_risk_level": self._calculate_overall_risk(all_anomalies),
            "recommended_actions": self._generate_recommended_actions(all_anomalies),
            "analysis_timestamp": datetime.utcnow().isoformat()
        }
    
    def _enhance_with_statistics(self, result: Dict, bid_responses: List) -> Dict:
        """Add statistical analysis to results."""
        if not bid_responses:
            return result
        
        # Extract prices
        prices = []
        for bid in bid_responses:
            price = bid.get("total_price", 0) or bid.get("price", 0)
            if price:
                prices.append(float(price))
        
        if prices:
            import statistics
            
            mean_price = statistics.mean(prices)
            median_price = statistics.median(prices)
            
            if len(prices) > 1:
                std_dev = statistics.stdev(prices)
            else:
                std_dev = 0
            
            # Identify outliers
            outliers = []
            for i, price in enumerate(prices):
                if abs(price - mean_price) > 2 * std_dev:
                    outliers.append({
                        "vendor": bid_responses[i].get("vendor_name", f"Vendor {i+1}"),
                        "price": price,
                        "deviation": abs(price - mean_price) / std_dev if std_dev > 0 else 0
                    })
            
            result["statistical_summary"] = {
                "total_bids": len(prices),
                "mean_price": round(mean_price, 2),
                "median_price": round(median_price, 2),
                "std_deviation": round(std_dev, 2),
                "price_range": {
                    "min": min(prices),
                    "max": max(prices)
                },
                "outliers": outliers
            }
        
        return result
    
    def _create_fallback_pricing_analysis(self, llm_response: str, bids: List) -> Dict:
        """Create fallback analysis structure."""
        return {
            "anomalies": [
                {
                    "anomaly_id": "REVIEW-001",
                    "anomaly_type": "manual_review",
                    "description": "Detailed manual review required",
                    "severity": "Medium",
                    "analysis_text": llm_response
                }
            ],
            "statistical_summary": {
                "total_bids": len(bids)
            },
            "status": "manual_review_required"
        }
    
    def _calculate_overall_risk(self, anomalies: List) -> str:
        """Calculate overall risk level from anomalies."""
        if not anomalies:
            return "Low"
        
        critical_count = len([a for a in anomalies if a.get("severity") == "Critical"])
        high_count = len([a for a in anomalies if a.get("severity") == "High"])
        
        if critical_count > 0:
            return "Critical"
        elif high_count > 2:
            return "High"
        elif high_count > 0 or len(anomalies) > 5:
            return "Medium"
        else:
            return "Low"
    
    def _generate_recommended_actions(self, anomalies: List) -> List[str]:
        """Generate recommended actions based on anomalies."""
        actions = []
        
        critical_anomalies = [a for a in anomalies if a.get("severity") == "Critical"]
        if critical_anomalies:
            actions.append("IMMEDIATE: Address all critical anomalies before proceeding")
        
        pricing_anomalies = [a for a in anomalies if "pricing" in a.get("anomaly_type", "").lower()]
        if pricing_anomalies:
            actions.append("Request detailed cost breakdowns from outlier bidders")
        
        compliance_issues = [a for a in anomalies if "compliance" in str(a).lower()]
        if compliance_issues:
            actions.append("Conduct compliance review before award")
        
        if not actions:
            actions.append("Proceed with standard evaluation process")
        
        return actions
    
    def _calculate_confidence(self, result: Dict) -> float:
        """Calculate confidence in anomaly detection."""
        confidence = 0.75  # Base confidence
        
        # Higher confidence with statistical backing
        if "statistical_summary" in result:
            confidence += 0.1
        
        # Higher confidence with multiple detection types
        if "comprehensive_analysis" in result:
            confidence += 0.1
        
        # Adjust for number of anomalies
        anomaly_count = len(result.get("anomalies", []))
        if anomaly_count > 0:
            confidence += 0.05
        
        return min(confidence, 0.95)


# Global RFQ/RFP anomaly agent instance
rfq_rfp_anomaly_agent = RFQRFPAnomalyAgent()
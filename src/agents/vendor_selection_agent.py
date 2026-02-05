"""
Vendor Selection & Shortlisting Agent - Optimizes vendor selection using weighted scoring,
risk flags identification, AI-based bid evaluation, and supplier reliability assessment.
"""
from typing import Dict, Any, List, Optional, Tuple
from datetime import datetime
import json
from src.utils.logging import get_logger
from src.models.core import AgentInput, AgentOutput
from src.core.llm_client import llm_client

logger = get_logger(__name__)


class VendorSelectionAgent:
    """
    Vendor Selection & Shortlisting Agent.
    Weighted scoring, risk assessment, bid evaluation, and reliability analysis.
    """
    
    name = "vendor_selection_agent"
    capabilities = [
        "vendor_shortlisting",
        "weighted_scoring",
        "risk_flag_identification",
        "bid_evaluation",
        "supplier_reliability_assessment",
        "multi_criteria_analysis",
        "vendor_ranking"
    ]
    
    async def execute(self, agent_input: AgentInput) -> AgentOutput:
        """Execute vendor selection and shortlisting."""
        start_time = datetime.utcnow()
        
        logger.info(
            "Vendor Selection agent executing",
            task_id=str(agent_input.task_id)
        )
        
        try:
            selection_type = agent_input.context.get("selection_type", "comprehensive")
            
            if selection_type == "shortlist":
                result = await self._shortlist_vendors(agent_input)
            elif selection_type == "weighted_scoring":
                result = await self._weighted_scoring_analysis(agent_input)
            elif selection_type == "risk_assessment":
                result = await self._identify_risk_flags(agent_input)
            elif selection_type == "bid_evaluation":
                result = await self._evaluate_bids(agent_input)
            elif selection_type == "reliability":
                result = await self._assess_supplier_reliability(agent_input)
            else:
                result = await self._comprehensive_vendor_selection(agent_input)
            
            confidence = self._calculate_confidence(result)
            sources = self._extract_sources(agent_input)
            
            execution_time = (datetime.utcnow() - start_time).total_seconds() * 1000
            
            logger.info(
                "Vendor Selection agent completed",
                task_id=str(agent_input.task_id),
                vendors_evaluated=result.get("total_vendors_evaluated", 0),
                shortlisted=len(result.get("shortlisted_vendors", [])),
                confidence=confidence
            )
            
            return AgentOutput(
                task_id=agent_input.task_id,
                agent_name=self.name,
                result=result,
                confidence=confidence,
                sources=sources,
                execution_time_ms=execution_time,
                metadata={
                    "selection_type": selection_type,
                    "vendors_evaluated": result.get("total_vendors_evaluated", 0),
                    "high_risk_count": len([v for v in result.get("vendor_scores", []) if v.get("risk_level") == "High"])
                }
            )
            
        except Exception as e:
            logger.error(
                "Vendor Selection agent failed",
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
    
    async def _shortlist_vendors(self, agent_input: AgentInput) -> Dict[str, Any]:
        """Shortlist vendors based on criteria."""
        vendors = agent_input.context.get("vendors", [])
        requirements = agent_input.context.get("requirements", {})
        shortlist_count = agent_input.context.get("shortlist_count", 5)
        
        memory_context_str = ""
        if agent_input.memory_context:
            memory_context_str = "\n\nHistorical Vendor Performance:\n" + "\n".join(
                [f"- {item.get('content', {})}" for item in agent_input.memory_context[:5]]
            )
        
        prompt = f"""Shortlist the best vendors based on requirements and evaluation.

Total Vendors: {len(vendors)}
Target Shortlist Count: {shortlist_count}

Requirements:
{json.dumps(requirements, indent=2)}

Vendor Information:
{json.dumps(vendors, indent=2)[:3000]}
{memory_context_str}

Instructions: {agent_input.instructions}

Evaluate each vendor on:
1. QUALIFICATION MATCH
   - Technical capabilities
   - Experience and track record
   - Certifications and licenses
   - References and past projects

2. FINANCIAL STABILITY
   - Financial health
   - Business continuity
   - Credit rating
   - Insurance coverage

3. CAPACITY AND RESOURCES
   - Workforce capacity
   - Equipment and facilities
   - Geographic coverage
   - Scalability

4. COMPLIANCE
   - Regulatory compliance
   - Safety record
   - Environmental compliance
   - Quality certifications

5. COMMERCIAL TERMS
   - Pricing competitiveness
   - Payment terms
   - Contract flexibility
   - Value-added services

Output JSON format:
{{
    "shortlisted_vendors": [
        {{
            "vendor_id": "ID",
            "vendor_name": "Name",
            "overall_score": 85.5,
            "ranking": 1,
            "strengths": ["Strength 1", "Strength 2"],
            "weaknesses": ["Weakness 1"],
            "risk_level": "Low/Medium/High",
            "recommendation": "Highly Recommended/Recommended/Conditional",
            "rationale": "Why this vendor is shortlisted",
            "scores": {{
                "qualification": 90,
                "financial": 85,
                "capacity": 80,
                "compliance": 95,
                "commercial": 75
            }}
        }}
    ],
    "eliminated_vendors": [
        {{
            "vendor_name": "Name",
            "elimination_reason": "Reason",
            "deficiencies": []
        }}
    ],
    "shortlisting_summary": {{
        "total_evaluated": 0,
        "shortlisted": 0,
        "eliminated": 0,
        "methodology": "Description"
    }}
}}

Shortlist Analysis:"""

        response = await llm_client.generate(prompt, temperature=0.3)
        
        try:
            start_idx = response.find('{')
            end_idx = response.rfind('}') + 1
            
            if start_idx >= 0 and end_idx > start_idx:
                json_str = response[start_idx:end_idx]
                result = json.loads(json_str)
            else:
                result = self._create_fallback_shortlist(vendors, shortlist_count)
            
            result["timestamp"] = datetime.utcnow().isoformat()
            result["total_vendors_evaluated"] = len(vendors)
            
            return result
            
        except json.JSONDecodeError:
            return self._create_fallback_shortlist(vendors, shortlist_count)
    
    async def _weighted_scoring_analysis(self, agent_input: AgentInput) -> Dict[str, Any]:
        """Perform weighted scoring analysis on vendors."""
        vendors = agent_input.context.get("vendors", [])
        scoring_criteria = agent_input.context.get("scoring_criteria", {})
        weights = agent_input.context.get("weights", {})
        
        # Default weights if not provided
        if not weights:
            weights = {
                "price": 0.30,
                "quality": 0.25,
                "experience": 0.20,
                "capacity": 0.15,
                "compliance": 0.10
            }
        
        prompt = f"""Perform weighted scoring analysis for vendor selection.

Scoring Criteria and Weights:
{json.dumps(weights, indent=2)}

Detailed Criteria:
{json.dumps(scoring_criteria, indent=2)}

Vendor Data:
{json.dumps(vendors, indent=2)[:3000]}

Instructions: {agent_input.instructions}

For each vendor, score on scale of 0-100 for each criterion:

1. PRICE (Weight: {weights.get('price', 0.30)})
   - Competitiveness
   - Value for money
   - Total cost of ownership

2. QUALITY (Weight: {weights.get('quality', 0.25)})
   - Quality certifications
   - Defect rates
   - Quality control processes

3. EXPERIENCE (Weight: {weights.get('experience', 0.20)})
   - Years in business
   - Similar project experience
   - Client references

4. CAPACITY (Weight: {weights.get('capacity', 0.15)})
   - Resource availability
   - Scalability
   - Delivery capability

5. COMPLIANCE (Weight: {weights.get('compliance', 0.10)})
   - Regulatory compliance
   - Certifications
   - Safety record

Calculate:
- Individual criterion scores
- Weighted scores
- Total weighted score
- Relative rankings

Output JSON:
{{
    "vendor_scores": [
        {{
            "vendor_id": "ID",
            "vendor_name": "Name",
            "criterion_scores": {{
                "price": 85,
                "quality": 90,
                "experience": 75,
                "capacity": 80,
                "compliance": 95
            }},
            "weighted_scores": {{
                "price": 25.5,
                "quality": 22.5,
                "experience": 15.0,
                "capacity": 12.0,
                "compliance": 9.5
            }},
            "total_weighted_score": 84.5,
            "rank": 1,
            "percentile": 95
        }}
    ],
    "scoring_summary": {{
        "weights_used": {{}},
        "highest_score": 0,
        "lowest_score": 0,
        "average_score": 0,
        "score_distribution": {{}}
    }},
    "sensitivity_analysis": {{
        "impact_of_price_weight": "Analysis",
        "critical_criteria": []
    }}
}}

Weighted Scoring:"""

        response = await llm_client.generate(prompt, temperature=0.2)
        
        try:
            start_idx = response.find('{')
            end_idx = response.rfind('}') + 1
            
            if start_idx >= 0 and end_idx > start_idx:
                json_str = response[start_idx:end_idx]
                result = json.loads(json_str)
            else:
                result = self._calculate_weighted_scores(vendors, weights)
            
            result["weights_used"] = weights
            result["total_vendors_evaluated"] = len(vendors)
            
            return result
            
        except json.JSONDecodeError:
            return self._calculate_weighted_scores(vendors, weights)
    
    async def _identify_risk_flags(self, agent_input: AgentInput) -> Dict[str, Any]:
        """Identify risk flags in vendor profiles."""
        vendors = agent_input.context.get("vendors", [])
        
        prompt = f"""Identify risk flags and concerns for each vendor.

Vendor Data:
{json.dumps(vendors, indent=2)[:3000]}

Instructions: {agent_input.instructions}

Identify risk flags in categories:

1. FINANCIAL RISKS
   - Poor financial health
   - Recent losses or bankruptcies
   - Inadequate insurance
   - Payment defaults

2. OPERATIONAL RISKS
   - Insufficient capacity
   - Limited resources
   - Geographic constraints
   - Technology limitations

3. COMPLIANCE RISKS
   - Regulatory violations
   - Missing certifications
   - Safety incidents
   - Legal disputes

4. PERFORMANCE RISKS
   - Poor track record
   - Customer complaints
   - Quality issues
   - Delivery failures

5. REPUTATION RISKS
   - Negative publicity
   - Ethical concerns
   - Environmental violations
   - Labor issues

6. RELATIONSHIP RISKS
   - Conflicts of interest
   - Dependency on single client
   - Key person dependency
   - Ownership changes

Output JSON:
{{
    "vendor_risk_assessments": [
        {{
            "vendor_name": "Name",
            "risk_level": "Critical/High/Medium/Low",
            "risk_flags": [
                {{
                    "flag_id": "RISK-001",
                    "category": "Financial/Operational/Compliance/etc",
                    "severity": "Critical/High/Medium/Low",
                    "description": "Description",
                    "evidence": "Evidence",
                    "mitigation": "How to mitigate",
                    "impact": "Potential impact"
                }}
            ],
            "risk_score": 65,
            "recommendation": "Proceed/Proceed with caution/Do not proceed"
        }}
    ],
    "summary": {{
        "high_risk_vendors": 0,
        "medium_risk_vendors": 0,
        "low_risk_vendors": 0,
        "common_risks": [],
        "critical_flags_requiring_attention": []
    }}
}}

Risk Assessment:"""

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
            "vendor_risk_assessments": [],
            "analysis": response,
            "total_vendors_evaluated": len(vendors)
        }
    
    async def _evaluate_bids(self, agent_input: AgentInput) -> Dict[str, Any]:
        """Evaluate vendor bids using AI analysis."""
        bids = agent_input.context.get("bids", [])
        evaluation_criteria = agent_input.context.get("evaluation_criteria", {})
        
        prompt = f"""Evaluate vendor bids comprehensively.

Bids:
{json.dumps(bids, indent=2)[:3000]}

Evaluation Criteria:
{json.dumps(evaluation_criteria, indent=2)}

Instructions: {agent_input.instructions}

Evaluate each bid on:

1. RESPONSIVENESS
   - Addresses all requirements
   - Complete documentation
   - Clear proposal structure
   - Compliance with instructions

2. TECHNICAL APPROACH
   - Methodology soundness
   - Innovation and value-add
   - Risk mitigation strategies
   - Implementation plan

3. COMMERCIAL TERMS
   - Pricing structure
   - Payment terms
   - Warranties and guarantees
   - Contract conditions

4. TEAM AND RESOURCES
   - Team qualifications
   - Resource allocation
   - Key personnel CVs
   - Subcontractor management

5. PAST PERFORMANCE
   - Relevant experience
   - Client references
   - Success metrics
   - Lessons learned

Output JSON:
{{
    "bid_evaluations": [
        {{
            "vendor_name": "Name",
            "bid_id": "ID",
            "scores": {{
                "responsiveness": 85,
                "technical_approach": 90,
                "commercial_terms": 80,
                "team_resources": 85,
                "past_performance": 88
            }},
            "total_score": 85.6,
            "rank": 1,
            "strengths": [],
            "weaknesses": [],
            "clarifications_needed": [],
            "recommendation": "Award/Shortlist/Reject"
        }}
    ],
    "comparative_analysis": {{
        "best_technical": "Vendor",
        "best_price": "Vendor",
        "best_value": "Vendor",
        "recommended_award": "Vendor"
    }}
}}

Bid Evaluation:"""

        response = await llm_client.generate(prompt, temperature=0.3)
        
        try:
            start_idx = response.find('{')
            end_idx = response.rfind('}') + 1
            
            if start_idx >= 0 and end_idx > start_idx:
                json_str = response[start_idx:end_idx]
                return json.loads(json_str)
        except json.JSONDecodeError:
            pass
        
        return {
            "bid_evaluations": [],
            "analysis": response,
            "total_bids_evaluated": len(bids)
        }
    
    async def _assess_supplier_reliability(self, agent_input: AgentInput) -> Dict[str, Any]:
        """Assess supplier reliability using historical data and performance metrics."""
        vendors = agent_input.context.get("vendors", [])
        performance_data = agent_input.context.get("performance_data", {})
        
        memory_context_str = ""
        if agent_input.memory_context:
            memory_context_str = "\n\nHistorical Performance Data:\n" + "\n".join(
                [f"- {item}" for item in agent_input.memory_context[:5]]
            )
        
        prompt = f"""Assess supplier reliability based on performance data.

Vendors:
{json.dumps(vendors, indent=2)[:2000]}

Performance Data:
{json.dumps(performance_data, indent=2)[:2000]}
{memory_context_str}

Instructions: {agent_input.instructions}

Assess reliability across:

1. DELIVERY PERFORMANCE
   - On-time delivery rate
   - Order fulfillment accuracy
   - Lead time consistency
   - Emergency response capability

2. QUALITY PERFORMANCE
   - Defect rate
   - Rejection rate
   - Warranty claims
   - Quality certifications maintenance

3. COMMUNICATION
   - Responsiveness
   - Proactive updates
   - Issue escalation
   - Documentation quality

4. FINANCIAL RELIABILITY
   - Payment consistency
   - Pricing stability
   - No hidden costs
   - Transparent billing

5. CONTINUOUS IMPROVEMENT
   - Process improvements
   - Technology adoption
   - Innovation suggestions
   - Corrective actions

Output JSON:
{{
    "reliability_assessments": [
        {{
            "vendor_name": "Name",
            "reliability_score": 85.5,
            "reliability_rating": "Excellent/Good/Fair/Poor",
            "metrics": {{
                "on_time_delivery": 95,
                "quality_score": 90,
                "communication_score": 85,
                "financial_score": 92,
                "improvement_score": 80
            }},
            "performance_trends": "Improving/Stable/Declining",
            "reliability_concerns": [],
            "strengths": [],
            "recommendation": "Preferred/Approved/Conditional/Not Recommended"
        }}
    ],
    "reliability_summary": {{
        "most_reliable": "Vendor",
        "least_reliable": "Vendor",
        "average_reliability": 0
    }}
}}

Reliability Assessment:"""

        response = await llm_client.generate(prompt, temperature=0.3)
        
        try:
            start_idx = response.find('{')
            end_idx = response.rfind('}') + 1
            
            if start_idx >= 0 and end_idx > start_idx:
                json_str = response[start_idx:end_idx]
                return json.loads(json_str)
        except json.JSONDecodeError:
            pass
        
        return {
            "reliability_assessments": [],
            "analysis": response,
            "total_vendors_evaluated": len(vendors)
        }
    
    async def _comprehensive_vendor_selection(self, agent_input: AgentInput) -> Dict[str, Any]:
        """Perform comprehensive vendor selection analysis."""
        # Combine all analyses
        shortlist_result = await self._shortlist_vendors(agent_input)
        scoring_result = await self._weighted_scoring_analysis(agent_input)
        risk_result = await self._identify_risk_flags(agent_input)
        reliability_result = await self._assess_supplier_reliability(agent_input)
        
        # Create final recommendation
        final_recommendation = self._create_final_recommendation(
            shortlist_result,
            scoring_result,
            risk_result,
            reliability_result
        )
        
        return {
            "comprehensive_analysis": {
                "shortlisting": shortlist_result,
                "weighted_scoring": scoring_result,
                "risk_assessment": risk_result,
                "reliability_assessment": reliability_result
            },
            "final_recommendation": final_recommendation,
            "total_vendors_evaluated": shortlist_result.get("total_vendors_evaluated", 0),
            "analysis_timestamp": datetime.utcnow().isoformat()
        }
    
    def _calculate_weighted_scores(self, vendors: List, weights: Dict) -> Dict:
        """Calculate weighted scores (fallback method)."""
        vendor_scores = []
        
        for vendor in vendors:
            # Simple scoring based on available data
            scores = {
                "price": 70,
                "quality": 75,
                "experience": 80,
                "capacity": 75,
                "compliance": 85
            }
            
            weighted_total = sum(scores[k] * weights.get(k, 0) for k in scores.keys())
            
            vendor_scores.append({
                "vendor_name": vendor.get("name", "Unknown"),
                "criterion_scores": scores,
                "total_weighted_score": round(weighted_total, 2),
                "rank": 0  # Will be calculated after sorting
            })
        
        # Sort and assign ranks
        vendor_scores.sort(key=lambda x: x["total_weighted_score"], reverse=True)
        for i, vendor in enumerate(vendor_scores):
            vendor["rank"] = i + 1
        
        return {
            "vendor_scores": vendor_scores,
            "weights_used": weights,
            "total_vendors_evaluated": len(vendors)
        }
    
    def _create_fallback_shortlist(self, vendors: List, count: int) -> Dict:
        """Create fallback shortlist."""
        return {
            "shortlisted_vendors": vendors[:count],
            "eliminated_vendors": vendors[count:],
            "total_vendors_evaluated": len(vendors),
            "shortlisting_summary": {
                "total_evaluated": len(vendors),
                "shortlisted": min(count, len(vendors)),
                "eliminated": max(0, len(vendors) - count)
            }
        }
    
    def _create_final_recommendation(
        self,
        shortlist: Dict,
        scoring: Dict,
        risk: Dict,
        reliability: Dict
    ) -> Dict:
        """Create final vendor selection recommendation."""
        shortlisted = shortlist.get("shortlisted_vendors", [])
        
        if not shortlisted:
            return {
                "recommended_vendor": None,
                "rationale": "No vendors met shortlisting criteria"
            }
        
        # Get top vendor from shortlist
        top_vendor = shortlisted[0] if shortlisted else {}
        
        return {
            "recommended_vendor": top_vendor.get("vendor_name", "Unknown"),
            "recommendation_strength": "Strong",
            "rationale": f"Top-ranked vendor with score {top_vendor.get('overall_score', 0)}",
            "alternatives": [v.get("vendor_name") for v in shortlisted[1:3]],
            "key_considerations": [
                "Review contract terms carefully",
                "Verify certifications and credentials",
                "Conduct reference checks",
                "Negotiate favorable payment terms"
            ]
        }
    
    def _calculate_confidence(self, result: Dict) -> float:
        """Calculate confidence in vendor selection."""
        confidence = 0.75
        
        if "comprehensive_analysis" in result:
            confidence += 0.15
        
        if result.get("vendor_scores") or result.get("shortlisted_vendors"):
            confidence += 0.05
        
        if result.get("final_recommendation"):
            confidence += 0.05
        
        return min(confidence, 0.95)
    
    def _extract_sources(self, agent_input: AgentInput) -> List[str]:
        """Extract sources from agent input."""
        sources = []
        
        if agent_input.memory_context:
            sources.append("Historical vendor performance data")
        
        if agent_input.context.get("vendors"):
            sources.append("Vendor profiles and documentation")
        
        return sources


# Global vendor selection agent instance
vendor_selection_agent = VendorSelectionAgent()
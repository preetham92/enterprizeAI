"""
Additional Specialized Agents - Contract Review, Change Orders, Predictive Analytics, Records Keeping
"""
from typing import Dict, Any, List, Optional
from datetime import datetime
import json
from src.utils.logging import get_logger
from src.models.core import AgentInput, AgentOutput
from src.core.llm_client import llm_client

logger = get_logger(__name__)


class ContractReviewAgent:
    """
    Contract Review Agent - Advanced GCC/SCC deviation detection with RAG flagging.
    """
    
    name = "contract_review_agent"
    capabilities = [
        "gcc_scc_deviation_detection",
        "rag_flagging",
        "clause_analysis",
        "risk_categorization",
        "compliance_verification"
    ]
    
    async def execute(self, agent_input: AgentInput) -> AgentOutput:
        """Execute contract review with GCC/SCC deviation detection."""
        start_time = datetime.utcnow()
        
        logger.info("Contract Review agent executing", task_id=str(agent_input.task_id))
        
        try:
            contract_text = agent_input.context.get("contract_text", "")
            gcc_template = agent_input.context.get("gcc_template", "")
            scc_template = agent_input.context.get("scc_template", "")
            
            memory_context_str = ""
            if agent_input.memory_context:
                memory_context_str = "\n\nHistorical Deviation Patterns:\n" + "\n".join(
                    [f"- {item}" for item in agent_input.memory_context[:3]]
                )
            
            prompt = f"""Review contract for GCC/SCC deviations and assign RAG flags.

Contract to Review:
{contract_text[:3000]}

GCC Template Reference:
{gcc_template[:1500]}

SCC Template Reference:
{scc_template[:1500]}
{memory_context_str}

Instructions: {agent_input.instructions}

Perform comprehensive review:

1. DEVIATION DETECTION
   - Identify all deviations from GCC/SCC
   - Categorize deviations by section
   - Assess materiality of each deviation

2. RAG FLAGGING (Red-Amber-Green)
   RED FLAGS (Critical - Deal Breakers):
   - Liability caps removed/reduced significantly
   - Payment terms unfavorable (>90 days)
   - Termination rights restricted
   - Indemnity clauses heavily modified
   - IP rights issues
   - Regulatory non-compliance
   
   AMBER FLAGS (Medium - Needs Negotiation):
   - Payment terms moderately unfavorable
   - Warranty modifications
   - Insurance coverage gaps
   - Scope ambiguities
   - Timeline concerns
   
   GREEN FLAGS (Low - Acceptable):
   - Minor wording changes
   - Administrative updates
   - Clarifications
   - Non-material modifications

3. CLAUSE-BY-CLAUSE ANALYSIS
   - Deviation description
   - Risk assessment
   - Business impact
   - Legal implications
   - Mitigation recommendations

4. COMPLIANCE CHECK
   - Regulatory requirements
   - Company policies
   - Industry standards
   - Legal requirements

Output JSON:
{{
    "review_summary": {{
        "total_deviations": 0,
        "red_flags": 0,
        "amber_flags": 0,
        "green_flags": 0,
        "overall_risk": "Critical/High/Medium/Low",
        "recommendation": "Reject/Negotiate/Accept with conditions/Accept"
    }},
    "deviations": [
        {{
            "deviation_id": "DEV-001",
            "section": "Section number and name",
            "clause_reference": "Clause ID",
            "rag_flag": "Red/Amber/Green",
            "deviation_type": "Addition/Deletion/Modification",
            "gcc_text": "Original GCC text",
            "contract_text": "Actual contract text",
            "description": "Clear description of deviation",
            "risk_level": "Critical/High/Medium/Low",
            "business_impact": "Impact description",
            "legal_implications": "Legal concerns",
            "financial_impact": "Estimated cost/savings",
            "mitigation_strategy": "How to address",
            "negotiation_priority": "Must fix/Should fix/Nice to fix",
            "alternative_language": "Suggested replacement text"
        }}
    ],
    "red_flag_summary": {{
        "count": 0,
        "critical_issues": [],
        "immediate_actions_required": []
    }},
    "amber_flag_summary": {{
        "count": 0,
        "negotiation_points": [],
        "suggested_responses": []
    }},
    "green_flag_summary": {{
        "count": 0,
        "acceptable_changes": []
    }},
    "compliance_check": {{
        "compliant": false,
        "violations": [],
        "remediation_steps": []
    }},
    "recommendations": [
        {{
            "recommendation": "Action to take",
            "priority": "Immediate/High/Medium/Low",
            "owner": "Who should handle",
            "timeline": "When to complete"
        }}
    ],
    "approval_recommendation": "Approve/Reject/Return for revision",
    "next_steps": []
}}

Contract Review:"""

            response = await llm_client.generate(prompt, temperature=0.2)
            
            try:
                start_idx = response.find('{')
                end_idx = response.rfind('}') + 1
                
                if start_idx >= 0 and end_idx > start_idx:
                    json_str = response[start_idx:end_idx]
                    result = json.loads(json_str)
                else:
                    result = {"review_summary": {}, "deviations": [], "analysis": response}
            except json.JSONDecodeError:
                result = {"review_summary": {}, "deviations": [], "analysis": response}
            
            result["review_timestamp"] = datetime.utcnow().isoformat()
            
            confidence = 0.85 if result.get("deviations") else 0.70
            
            execution_time = (datetime.utcnow() - start_time).total_seconds() * 1000
            
            return AgentOutput(
                task_id=agent_input.task_id,
                agent_name=self.name,
                result=result,
                confidence=confidence,
                execution_time_ms=execution_time,
                metadata={
                    "red_flags": result.get("review_summary", {}).get("red_flags", 0),
                    "total_deviations": result.get("review_summary", {}).get("total_deviations", 0)
                }
            )
            
        except Exception as e:
            logger.error("Contract Review agent failed", error=str(e))
            execution_time = (datetime.utcnow() - start_time).total_seconds() * 1000
            
            return AgentOutput(
                task_id=agent_input.task_id,
                agent_name=self.name,
                result={},
                confidence=0.0,
                errors=[str(e)],
                execution_time_ms=execution_time
            )


class ChangeOrderAgent:
    """
    Variations/Change Orders Agent - Analyzes cost and scope impact.
    """
    
    name = "change_order_agent"
    capabilities = [
        "change_order_analysis",
        "cost_impact_assessment",
        "scope_impact_analysis",
        "timeline_impact_evaluation",
        "approval_recommendation"
    ]
    
    async def execute(self, agent_input: AgentInput) -> AgentOutput:
        """Execute change order analysis."""
        start_time = datetime.utcnow()
        
        logger.info("Change Order agent executing", task_id=str(agent_input.task_id))
        
        try:
            change_order = agent_input.context.get("change_order", {})
            original_contract = agent_input.context.get("original_contract", {})
            
            prompt = f"""Analyze change order/variation for cost and scope impact.

Change Order Details:
{json.dumps(change_order, indent=2)}

Original Contract:
{json.dumps(original_contract, indent=2)[:2000]}

Instructions: {agent_input.instructions}

Perform comprehensive impact analysis:

1. SCOPE IMPACT
   - Changes to deliverables
   - Work added/removed
   - Quality implications
   - Resource requirements

2. COST IMPACT
   - Direct cost changes
   - Indirect cost implications
   - Contingency impact
   - Budget variance
   - Cash flow effect

3. TIMELINE IMPACT
   - Schedule delays/acceleration
   - Milestone impact
   - Critical path changes
   - Dependency effects

4. RISK IMPACT
   - New risks introduced
   - Risk mitigation costs
   - Contractual risks
   - Performance risks

5. APPROVAL ANALYSIS
   - Approval requirements
   - Authority levels
   - Documentation needed
   - Stakeholder impacts

Output JSON:
{{
    "change_order_summary": {{
        "change_order_id": "CO-001",
        "description": "Summary",
        "change_category": "Scope/Cost/Timeline/Quality",
        "urgency": "Critical/High/Medium/Low"
    }},
    "cost_impact": {{
        "original_cost": 1000000,
        "change_order_cost": 150000,
        "revised_total_cost": 1150000,
        "cost_increase_percentage": 15.0,
        "cost_breakdown": {{
            "labor": 80000,
            "materials": 50000,
            "equipment": 15000,
            "overhead": 5000
        }},
        "justification": "Why costs increased",
        "cost_reasonableness": "Reasonable/Questionable/Excessive"
    }},
    "scope_impact": {{
        "scope_changes": [
            {{
                "item": "Item description",
                "change_type": "Addition/Deletion/Modification",
                "impact": "High/Medium/Low",
                "rationale": "Why needed"
            }}
        ],
        "deliverable_impact": "How deliverables affected",
        "quality_implications": "Quality considerations"
    }},
    "timeline_impact": {{
        "original_duration": "12 months",
        "time_extension": "2 months",
        "revised_duration": "14 months",
        "milestone_impacts": [
            {{
                "milestone": "Name",
                "original_date": "2026-06-01",
                "revised_date": "2026-08-01",
                "impact": "Critical path/Not critical"
            }}
        ],
        "schedule_risk": "High/Medium/Low"
    }},
    "risk_assessment": {{
        "new_risks": [],
        "risk_mitigation_cost": 0,
        "overall_risk": "High/Medium/Low"
    }},
    "approval_recommendation": {{
        "recommendation": "Approve/Reject/Negotiate/Defer",
        "rationale": "Why this recommendation",
        "conditions": "Conditions for approval",
        "approval_authority": "Who should approve",
        "supporting_documents": []
    }},
    "negotiation_points": [
        {{
            "item": "Cost element",
            "concern": "Why negotiate",
            "target": "Desired outcome"
        }}
    ],
    "alternative_solutions": []
}}

Change Order Analysis:"""

            response = await llm_client.generate(prompt, temperature=0.3)
            
            try:
                start_idx = response.find('{')
                end_idx = response.rfind('}') + 1
                
                if start_idx >= 0 and end_idx > start_idx:
                    json_str = response[start_idx:end_idx]
                    result = json.loads(json_str)
                else:
                    result = {"change_order_summary": {}, "analysis": response}
            except json.JSONDecodeError:
                result = {"change_order_summary": {}, "analysis": response}
            
            result["analysis_timestamp"] = datetime.utcnow().isoformat()
            
            confidence = 0.80
            execution_time = (datetime.utcnow() - start_time).total_seconds() * 1000
            
            return AgentOutput(
                task_id=agent_input.task_id,
                agent_name=self.name,
                result=result,
                confidence=confidence,
                execution_time_ms=execution_time
            )
            
        except Exception as e:
            logger.error("Change Order agent failed", error=str(e))
            execution_time = (datetime.utcnow() - start_time).total_seconds() * 1000
            
            return AgentOutput(
                task_id=agent_input.task_id,
                agent_name=self.name,
                result={},
                confidence=0.0,
                errors=[str(e)],
                execution_time_ms=execution_time
            )


class PredictiveAnalyticsAgent:
    """
    Predictive Analytics Agent - Forecasts costs, vendor performance, and timelines.
    """
    
    name = "predictive_analytics_agent"
    capabilities = [
        "cost_forecasting",
        "vendor_performance_prediction",
        "timeline_forecasting",
        "risk_prediction",
        "trend_analysis"
    ]
    
    async def execute(self, agent_input: AgentInput) -> AgentOutput:
        """Execute predictive analytics."""
        start_time = datetime.utcnow()
        
        logger.info("Predictive Analytics agent executing", task_id=str(agent_input.task_id))
        
        try:
            historical_data = agent_input.context.get("historical_data", {})
            forecast_type = agent_input.context.get("forecast_type", "comprehensive")
            
            memory_context_str = ""
            if agent_input.memory_context:
                memory_context_str = "\n\nHistorical Trends:\n" + "\n".join(
                    [f"- {item}" for item in agent_input.memory_context[:5]]
                )
            
            prompt = f"""Perform predictive analytics and forecasting.

Historical Data:
{json.dumps(historical_data, indent=2)[:3000]}

Forecast Type: {forecast_type}
{memory_context_str}

Instructions: {agent_input.instructions}

Provide forecasts for:

1. MATERIAL COST FORECASTING
   - Historical cost trends
   - Market analysis
   - Price predictions (3/6/12 months)
   - Confidence intervals
   - Cost drivers

2. VENDOR PERFORMANCE PREDICTION
   - On-time delivery forecast
   - Quality score predictions
   - Reliability assessment
   - Risk indicators

3. PROJECT TIMELINE FORECASTING
   - Completion date predictions
   - Milestone achievement probability
   - Delay risk factors
   - Acceleration opportunities

4. TREND ANALYSIS
   - Emerging patterns
   - Seasonal variations
   - Market shifts
   - Risk trends

Output JSON:
{{
    "material_cost_forecast": {{
        "material_type": "Type",
        "current_price": 100,
        "forecasts": [
            {{
                "period": "3 months",
                "predicted_price": 105,
                "confidence_interval": {{
                    "lower": 102,
                    "upper": 108
                }},
                "confidence_level": 0.85,
                "trend": "Increasing/Stable/Decreasing",
                "drivers": ["Factor 1", "Factor 2"]
            }}
        ],
        "recommendation": "Buy now/Wait/Hedge"
    }},
    "vendor_performance_forecast": {{
        "vendor_name": "Name",
        "forecasts": {{
            "on_time_delivery_rate": {{
                "current": 0.95,
                "predicted_3m": 0.93,
                "confidence": 0.80,
                "trend": "Declining"
            }},
            "quality_score": {{
                "current": 4.5,
                "predicted_3m": 4.3,
                "confidence": 0.75
            }},
            "risk_level": "Increasing/Stable/Decreasing"
        }}
    }},
    "timeline_forecast": {{
        "project": "Project name",
        "original_completion": "2026-12-31",
        "predicted_completion": "2027-02-15",
        "delay_probability": 0.65,
        "critical_milestones": [
            {{
                "milestone": "Name",
                "scheduled": "2026-06-01",
                "predicted": "2026-07-15",
                "risk": "High/Medium/Low"
            }}
        ],
        "acceleration_options": []
    }},
    "trend_analysis": {{
        "key_trends": [],
        "emerging_risks": [],
        "opportunities": []
    }},
    "recommendations": []
}}

Predictive Analysis:"""

            response = await llm_client.generate(prompt, temperature=0.4)
            
            try:
                start_idx = response.find('{')
                end_idx = response.rfind('}') + 1
                
                if start_idx >= 0 and end_idx > start_idx:
                    json_str = response[start_idx:end_idx]
                    result = json.loads(json_str)
                else:
                    result = {"forecast_summary": {}, "analysis": response}
            except json.JSONDecodeError:
                result = {"forecast_summary": {}, "analysis": response}
            
            result["forecast_timestamp"] = datetime.utcnow().isoformat()
            
            confidence = 0.70  # Forecasts are inherently less certain
            execution_time = (datetime.utcnow() - start_time).total_seconds() * 1000
            
            return AgentOutput(
                task_id=agent_input.task_id,
                agent_name=self.name,
                result=result,
                confidence=confidence,
                execution_time_ms=execution_time
            )
            
        except Exception as e:
            logger.error("Predictive Analytics agent failed", error=str(e))
            execution_time = (datetime.utcnow() - start_time).total_seconds() * 1000
            
            return AgentOutput(
                task_id=agent_input.task_id,
                agent_name=self.name,
                result={},
                confidence=0.0,
                errors=[str(e)],
                execution_time_ms=execution_time
            )


class RecordsKeepingAgent:
    """
    Records Keeping Agent - Maintains itemized benchmarking of all executed and current projects.
    """
    
    name = "records_keeping_agent"
    capabilities = [
        "project_benchmarking",
        "performance_tracking",
        "cost_tracking",
        "vendor_history",
        "lessons_learned",
        "kpi_monitoring"
    ]
    
    async def execute(self, agent_input: AgentInput) -> AgentOutput:
        """Execute records keeping and benchmarking."""
        start_time = datetime.utcnow()
        
        logger.info("Records Keeping agent executing", task_id=str(agent_input.task_id))
        
        try:
            record_type = agent_input.context.get("record_type", "project_benchmark")
            project_data = agent_input.context.get("project_data", {})
            
            if record_type == "project_benchmark":
                result = await self._create_project_benchmark(agent_input, project_data)
            elif record_type == "vendor_history":
                result = await self._track_vendor_history(agent_input, project_data)
            elif record_type == "performance_metrics":
                result = await self._track_performance_metrics(agent_input, project_data)
            else:
                result = await self._comprehensive_record(agent_input, project_data)
            
            # Store in memory for future reference
            result["stored_for_benchmarking"] = True
            result["record_timestamp"] = datetime.utcnow().isoformat()
            
            confidence = 0.90  # High confidence in record keeping
            execution_time = (datetime.utcnow() - start_time).total_seconds() * 1000
            
            return AgentOutput(
                task_id=agent_input.task_id,
                agent_name=self.name,
                result=result,
                confidence=confidence,
                execution_time_ms=execution_time
            )
            
        except Exception as e:
            logger.error("Records Keeping agent failed", error=str(e))
            execution_time = (datetime.utcnow() - start_time).total_seconds() * 1000
            
            return AgentOutput(
                task_id=agent_input.task_id,
                agent_name=self.name,
                result={},
                confidence=0.0,
                errors=[str(e)],
                execution_time_ms=execution_time
            )
    
    async def _create_project_benchmark(self, agent_input: AgentInput, project_data: Dict) -> Dict:
        """Create itemized project benchmark."""
        prompt = f"""Create comprehensive project benchmark record.

Project Data:
{json.dumps(project_data, indent=2)[:2000]}

Instructions: {agent_input.instructions}

Create detailed benchmark with:
- All cost items
- Timeline metrics
- Quality metrics
- Vendor performance
- Lessons learned

Output JSON with complete itemization."""

        response = await llm_client.generate(prompt, temperature=0.3)
        
        return {
            "project_benchmark": {
                "project_id": project_data.get("project_id", "PROJ-001"),
                "project_name": project_data.get("name", "Unknown"),
                "cost_breakdown": project_data.get("costs", {}),
                "timeline_metrics": project_data.get("timeline", {}),
                "vendor_performance": project_data.get("vendors", {}),
                "quality_metrics": project_data.get("quality", {}),
                "lessons_learned": [],
                "benchmarking_notes": response[:500]
            }
        }
    
    async def _track_vendor_history(self, agent_input: AgentInput, data: Dict) -> Dict:
        """Track vendor performance history."""
        return {
            "vendor_history": {
                "vendor_name": data.get("vendor", "Unknown"),
                "projects": data.get("projects", []),
                "performance_summary": {},
                "trends": []
            }
        }
    
    async def _track_performance_metrics(self, agent_input: AgentInput, data: Dict) -> Dict:
        """Track comprehensive performance metrics."""
        return {
            "performance_metrics": {
                "kpis": data.get("kpis", {}),
                "trends": [],
                "benchmarks": {}
            }
        }
    
    async def _comprehensive_record(self, agent_input: AgentInput, data: Dict) -> Dict:
        """Create comprehensive record."""
        benchmark = await self._create_project_benchmark(agent_input, data)
        vendor = await self._track_vendor_history(agent_input, data)
        metrics = await self._track_performance_metrics(agent_input, data)
        
        return {
            "comprehensive_record": {
                "benchmark": benchmark,
                "vendor_history": vendor,
                "performance_metrics": metrics
            }
        }


# Global agent instances
contract_review_agent = ContractReviewAgent()
change_order_agent = ChangeOrderAgent()
predictive_analytics_agent = PredictiveAnalyticsAgent()
records_keeping_agent = RecordsKeepingAgent()
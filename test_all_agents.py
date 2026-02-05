"""
Comprehensive Test Script for AI Orchestration Platform
Tests individual Agents and the Central Orchestrator.
Updated for consistency with core.py and orchestrator.py
"""
import asyncio
import sys
import json
from datetime import datetime
from typing import Dict, Any
from uuid import uuid4

# Add src to path for imports - Adjust if your project root differs
sys.path.insert(0, '/home/claude/ai-orchestration-platform')

# --- Core Model Imports ---
from src.models.core import (
    AgentInput, 
    TaskType, 
    OrchestratorRequest, 
    OrchestratorResponse
)
from src.orchestrator.orchestrator import Orchestrator

# --- Agent Imports ---
# Assuming these exist in your structure based on the previous file
from src.agents.search_agent import search_agent
from src.agents.document_automation_agent import document_automation_agent
from src.agents.rfq_rfp_anomaly_agent import rfq_rfp_anomaly_agent
from src.agents.vendor_selection_agent import vendor_selection_agent
from src.agents.negotiation_strategy_agent_enhanced import negotiation_strategy_agent_enhanced
from src.agents.document_contract_agent import document_contract_agent

# Specialized Agents imports
from src.agents.additional_specialized_agent import (
    contract_review_agent,
    change_order_agent,
    predictive_analytics_agent,
    records_keeping_agent
)
from src.agents.specialized_agent import (
    risk_compliance_agent,
    negotiation_strategy_agent,
    analytics_forecast_agent,
    fraud_anomaly_agent
)


class AgentTester:
    """Comprehensive testing suite for Agents and Orchestrator."""
    
    def __init__(self):
        self.results = []
        self.passed = 0
        self.failed = 0
    
    def print_header(self, text: str):
        """Print formatted header."""
        print("\n" + "="*80)
        print(f"  {text}")
        print("="*80)
    
    def print_result(self, name: str, status: str, message: str):
        """Print test result."""
        symbol = "✅" if status == "PASS" else "❌"
        print(f"{symbol} {name:40s} {status:6s} - {message}")
    
    async def test_agent(
        self,
        agent_name: str,
        agent,
        agent_input: AgentInput
    ) -> Dict[str, Any]:
        """Test a single agent execution."""
        try:
            # Execute Agent
            output = await agent.execute(agent_input)
            
            # Validate output against AgentOutput model in core.py
            assert hasattr(output, 'task_id'), "Missing task_id"
            assert hasattr(output, 'agent_name'), "Missing agent_name"
            assert hasattr(output, 'result'), "Missing result"
            assert hasattr(output, 'confidence'), "Missing confidence"
            assert 0.0 <= output.confidence <= 1.0, "Invalid confidence score"
            
            self.passed += 1
            execution_time = output.execution_time_ms if output.execution_time_ms else 0
            
            self.print_result(
                agent_name,
                "PASS",
                f"Confidence: {output.confidence:.2f}, Time: {execution_time:.0f}ms"
            )
            
            return {
                "status": "PASS",
                "agent_name": agent_name,
                "confidence": output.confidence,
                "execution_time": execution_time,
                "result_preview": str(output.result)[:100] + "...",
                "errors": output.errors
            }
            
        except Exception as e:
            self.failed += 1
            self.print_result(agent_name, "FAIL", str(e))
            return {
                "status": "FAIL",
                "agent_name": agent_name,
                "error": str(e)
            }

    async def test_orchestrator(self) -> Dict[str, Any]:
        """Test the Central Orchestrator flow."""
        agent_name = "Orchestrator Integration"
        try:
            orchestrator = Orchestrator()
            
            # Create Request
            request = OrchestratorRequest(
                user_query="Check this contract for liability risks and negotiate better terms.",
                document_text="The Provider's liability shall be limited to $100. Payment is Net 90.",
                domain_context={"priority": "high"}
            )
            
            # Execute Orchestrator
            response: OrchestratorResponse = await orchestrator.process_request(request)
            
            # Validate Response Structure
            assert isinstance(response, OrchestratorResponse), "Invalid response type"
            assert response.request_id == request.request_id, "Request ID mismatch"
            assert len(response.agent_outputs) > 0, "No agents were triggered"
            assert response.confidence >= 0.0, "Invalid confidence"
            
            self.passed += 1
            self.print_result(
                agent_name, 
                "PASS", 
                f"Agents Triggered: {len(response.agent_outputs)}, Conf: {response.confidence:.2f}"
            )
            
            return {
                "status": "PASS",
                "agent_name": agent_name,
                "confidence": response.confidence,
                "execution_time": response.execution_time_ms,
                "result_preview": str(response.response)[:100] + "...",
                "metadata": response.metadata
            }
            
        except Exception as e:
            self.failed += 1
            self.print_result(agent_name, "FAIL", str(e))
            return {
                "status": "FAIL",
                "agent_name": agent_name,
                "error": str(e)
            }
    
    async def test_all_components(self):
        """Test all 14 agents + Orchestrator."""
        
        self.print_header("TESTING AI ORCHESTRATION PLATFORM")
        print(f"Start Time: {datetime.utcnow().isoformat()}")
        
        # ===================================================================
        # TEST 1: SEARCH AGENT
        # ===================================================================
        self.print_header("TEST 1: Search Agent")
        self.results.append(await self.test_agent(
            "Search Agent",
            search_agent,
            AgentInput(
                task_type=TaskType.SEARCH,
                context={"search_query": "construction materials suppliers Mumbai"},
                instructions="Search for suppliers"
            )
        ))
        
        # ===================================================================
        # TEST 2: DOCUMENT AUTOMATION AGENT
        # ===================================================================
        self.print_header("TEST 2: Document Automation Agent")
        self.results.append(await self.test_agent(
            "Document Automation Agent",
            document_automation_agent,
            AgentInput(
                task_type=TaskType.DOCUMENT_ANALYSIS,
                context={
                    "automation_type": "contract_generation",
                    "contract_type": "service_agreement",
                    "parties": {"client": "ABC Corp", "provider": "XYZ Ltd"},
                    "requirements": {"value": 500000}
                },
                instructions="Generate service agreement"
            )
        ))
        
        # ===================================================================
        # TEST 3: RFQ/RFP ANOMALY AGENT
        # ===================================================================
        self.print_header("TEST 3: RFQ/RFP Anomaly Agent")
        self.results.append(await self.test_agent(
            "RFQ/RFP Anomaly Agent",
            rfq_rfp_anomaly_agent,
            AgentInput(
                task_type=TaskType.FRAUD_DETECTION,
                context={
                    "detection_type": "pricing",
                    "rfq_data": {"item": "Steel", "quantity": 1000},
                    "bid_responses": [
                        {"vendor": "A", "unit_price": 450},
                        {"vendor": "B", "unit_price": 250} # Anomaly
                    ],
                    "historical_data": {"average_unit_price": 470}
                },
                instructions="Detect pricing anomalies"
            )
        ))
        
        # ===================================================================
        # TEST 4: VENDOR SELECTION AGENT
        # ===================================================================
        self.print_header("TEST 4: Vendor Selection Agent")
        self.results.append(await self.test_agent(
            "Vendor Selection Agent",
            vendor_selection_agent,
            AgentInput(
                task_type=TaskType.ANALYTICS_FORECAST,
                context={
                    "selection_type": "weighted_scoring",
                    "vendors": [{"id": "V1", "score": 80}, {"id": "V2", "score": 90}],
                    "weights": {"price": 0.5, "quality": 0.5}
                },
                instructions="Select best vendor"
            )
        ))
        
        # ===================================================================
        # TEST 5: ENHANCED NEGOTIATION AGENT
        # ===================================================================
        self.print_header("TEST 5: Enhanced Negotiation Agent")
        self.results.append(await self.test_agent(
            "Enhanced Negotiation Agent",
            negotiation_strategy_agent_enhanced,
            AgentInput(
                task_type=TaskType.NEGOTIATION_STRATEGY,
                context={
                    "strategy_type": "counter_offer",
                    "original_offer": {"price": 3000000},
                    "our_position": {"target_price": 2500000}
                },
                instructions="Generate counter-offer"
            )
        ))
        
        # ===================================================================
        # TEST 6: CONTRACT REVIEW AGENT
        # ===================================================================
        self.print_header("TEST 6: Contract Review Agent")
        self.results.append(await self.test_agent(
            "Contract Review Agent",
            contract_review_agent,
            AgentInput(
                task_type=TaskType.DOCUMENT_ANALYSIS,
                context={
                    "contract_text": "Liability limited to $500.",
                    "gcc_template": "Liability up to 100% of contract.",
                },
                instructions="Review for deviations"
            )
        ))
        
        # ===================================================================
        # TEST 7: CHANGE ORDER AGENT
        # ===================================================================
        self.print_header("TEST 7: Change Order Agent")
        self.results.append(await self.test_agent(
            "Change Order Agent",
            change_order_agent,
            AgentInput(
                task_type=TaskType.ANALYTICS_FORECAST,
                context={
                    "change_order": {"cost": 150000, "impact": "high"},
                    "original_contract": {"value": 1000000}
                },
                instructions="Analyze change order impact"
            )
        ))
        
        # ===================================================================
        # TEST 8: PREDICTIVE ANALYTICS AGENT
        # ===================================================================
        self.print_header("TEST 8: Predictive Analytics Agent")
        self.results.append(await self.test_agent(
            "Predictive Analytics Agent",
            predictive_analytics_agent,
            AgentInput(
                task_type=TaskType.ANALYTICS_FORECAST,
                context={
                    "forecast_type": "comprehensive",
                    "historical_data": {"prices": [100, 110, 120]}
                },
                instructions="Forecast costs"
            )
        ))
        
        # ===================================================================
        # TEST 9: RECORDS KEEPING AGENT
        # ===================================================================
        self.print_header("TEST 9: Records Keeping Agent")
        self.results.append(await self.test_agent(
            "Records Keeping Agent",
            records_keeping_agent,
            AgentInput(
                task_type=TaskType.ANALYTICS_FORECAST,
                context={
                    "record_type": "project_benchmark",
                    "project_data": {"id": "P1", "cost": 1000}
                },
                instructions="Create benchmark"
            )
        ))
        
        # ===================================================================
        # TEST 10: DOCUMENT/CONTRACT AGENT
        # ===================================================================
        self.print_header("TEST 10: Document/Contract Agent")
        self.results.append(await self.test_agent(
            "Document/Contract Agent",
            document_contract_agent,
            AgentInput(
                task_type=TaskType.DOCUMENT_ANALYSIS,
                context={
                    "document_text": "Agreement for IT services...",
                    "analysis_type": "clause_extraction"
                },
                instructions="Extract clauses"
            )
        ))
        
        # ===================================================================
        # TEST 11: RISK & COMPLIANCE AGENT
        # ===================================================================
        self.print_header("TEST 11: Risk & Compliance Agent")
        self.results.append(await self.test_agent(
            "Risk & Compliance Agent",
            risk_compliance_agent,
            AgentInput(
                task_type=TaskType.RISK_COMPLIANCE,
                context={
                    "data": "High risk terms detected",
                    "risk_type": "legal"
                },
                instructions="Assess risks"
            )
        ))
        
        # ===================================================================
        # TEST 12: BASIC NEGOTIATION AGENT
        # ===================================================================
        self.print_header("TEST 12: Basic Negotiation Agent")
        self.results.append(await self.test_agent(
            "Basic Negotiation Agent",
            negotiation_strategy_agent,
            AgentInput(
                task_type=TaskType.NEGOTIATION_STRATEGY,
                context={
                    "proposal": "$5M offer",
                    "objectives": ["Reduce cost"]
                },
                instructions="Develop strategy"
            )
        ))
        
        # ===================================================================
        # TEST 13: ANALYTICS & FORECAST AGENT
        # ===================================================================
        self.print_header("TEST 13: Analytics & Forecast Agent")
        self.results.append(await self.test_agent(
            "Analytics & Forecast Agent",
            analytics_forecast_agent,
            AgentInput(
                task_type=TaskType.ANALYTICS_FORECAST,
                context={
                    "historical_data": "Project durations: 12, 14, 13 months",
                    "forecast_type": "timeline"
                },
                instructions="Forecast timeline"
            )
        ))
        
        # ===================================================================
        # TEST 14: FRAUD & ANOMALY AGENT
        # ===================================================================
        self.print_header("TEST 14: Fraud & Anomaly Agent")
        self.results.append(await self.test_agent(
            "Fraud & Anomaly Agent",
            fraud_anomaly_agent,
            AgentInput(
                task_type=TaskType.FRAUD_DETECTION,
                context={
                    "transaction_data": "Invoice $500k vs typical $50k",
                    "detection_type": "invoice_fraud"
                },
                instructions="Detect fraud"
            )
        ))

        # ===================================================================
        # TEST 15: ORCHESTRATOR INTEGRATION TEST
        # ===================================================================
        self.print_header("TEST 15: ORCHESTRATOR FULL FLOW")
        self.results.append(await self.test_orchestrator())
        
        # ===================================================================
        # SUMMARY
        # ===================================================================
        self.print_summary()
    
    def print_summary(self):
        """Print test summary."""
        self.print_header("TEST SUMMARY")
        
        total = self.passed + self.failed
        success_rate = (self.passed / total * 100) if total > 0 else 0
        
        print(f"\nTotal Tests Run: {total}")
        print(f"✅ Passed: {self.passed}")
        print(f"❌ Failed: {self.failed}")
        print(f"Success Rate: {success_rate:.1f}%")
        
        if self.failed == 0:
            print("\n🎉 ALL TESTS PASSED! SYSTEM PRODUCTION READY 🎉")
        else:
            print(f"\n⚠️  {self.failed} test(s) failed. Check logs.")
            
        self.save_results()
    
    def save_results(self):
        """Save results to JSON."""
        timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
        filename = f"/home/claude/ai-orchestration-platform/test_results_{timestamp}.json"
        
        data = {
            "timestamp": datetime.utcnow().isoformat(),
            "summary": {
                "total": self.passed + self.failed,
                "passed": self.passed,
                "failed": self.failed
            },
            "results": self.results
        }
        
        with open(filename, 'w') as f:
            json.dump(data, f, indent=2, default=str)
        print(f"\n📄 Results saved to: {filename}")


async def main():
    """Main entry point."""
    tester = AgentTester()
    try:
        await tester.test_all_components()
    except Exception as e:
        print(f"\n❌ CRITICAL SUITE ERROR: {str(e)}")
        import traceback
        traceback.print_exc()
        return 1
    return 0 if tester.failed == 0 else 1


if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)
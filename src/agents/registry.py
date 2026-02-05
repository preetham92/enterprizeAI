"""
Agent Registry - Central registry for all agents in the system.
Provides unified interface for agent discovery and invocation.
"""
from typing import Dict, List, Any, Optional
from src.models.core import AgentInput, AgentOutput, TaskType
from src.agents.search_agent import search_agent
from src.agents.memory_agent import memory_agent
from src.agents.document_contract_agent import document_contract_agent
from src.agents.specialized_agent import (
    risk_compliance_agent,
    negotiation_strategy_agent,
    analytics_forecast_agent,
    fraud_anomaly_agent
)
# New specialized agents
from src.agents.document_automation_agent import document_automation_agent
from src.agents.rfq_rfp_anomaly_agent import rfq_rfp_anomaly_agent
from src.agents.vendor_selection_agent import vendor_selection_agent
from src.agents.negotiation_strategy_agent_enhanced import negotiation_strategy_agent_enhanced
from src.agents.additional_specialized_agent import (
    contract_review_agent,
    change_order_agent,
    predictive_analytics_agent,
    records_keeping_agent
)
from src.utils.logging import get_logger

logger = get_logger(__name__)


class AgentRegistry:
    """
    Central registry for all agents.
    Maps task types to appropriate agents.
    """
    
    def __init__(self):
        # Register all agents
        self.agents = {
            "search_agent": search_agent,
            "memory_agent": memory_agent,
            "document_contract_agent": document_contract_agent,
            "risk_compliance_agent": risk_compliance_agent,
            "negotiation_strategy_agent": negotiation_strategy_agent,
            "analytics_forecast_agent": analytics_forecast_agent,
            "fraud_anomaly_agent": fraud_anomaly_agent,
            # New agents
            "document_automation_agent": document_automation_agent,
            "rfq_rfp_anomaly_agent": rfq_rfp_anomaly_agent,
            "vendor_selection_agent": vendor_selection_agent,
            "negotiation_strategy_agent_enhanced": negotiation_strategy_agent_enhanced,
            "contract_review_agent": contract_review_agent,
            "change_order_agent": change_order_agent,
            "predictive_analytics_agent": predictive_analytics_agent,
            "records_keeping_agent": records_keeping_agent
        }
        
        # Map task types to agents
        self.task_agent_mapping = {
            TaskType.SEARCH: ["search_agent"],
            TaskType.DOCUMENT_ANALYSIS: ["document_contract_agent"],
            TaskType.RISK_COMPLIANCE: ["risk_compliance_agent"],
            TaskType.NEGOTIATION_STRATEGY: ["negotiation_strategy_agent"],
            TaskType.ANALYTICS_FORECAST: ["analytics_forecast_agent"],
            TaskType.FRAUD_DETECTION: ["fraud_anomaly_agent"],
            TaskType.MEMORY_RETRIEVAL: ["memory_agent"],
            TaskType.MEMORY_STORAGE: ["memory_agent"]
        }
        
        logger.info("Agent registry initialized", agent_count=len(self.agents))
    
    def get_agent(self, agent_name: str):
        """Get agent by name."""
        agent = self.agents.get(agent_name)
        if not agent:
            raise ValueError(f"Agent '{agent_name}' not found in registry")
        return agent
    
    def get_agents_for_task(self, task_type: TaskType) -> List[Any]:
        """Get appropriate agents for a task type."""
        agent_names = self.task_agent_mapping.get(task_type, [])
        return [self.agents[name] for name in agent_names if name in self.agents]
    
    def list_all_agents(self) -> List[Dict[str, Any]]:
        """List all registered agents with their capabilities."""
        return [
            {
                "name": agent.name,
                "capabilities": agent.capabilities
            }
            for agent in self.agents.values()
        ]
    
    def get_agent_by_capability(self, capability: str) -> List[Any]:
        """Find agents that have a specific capability."""
        matching_agents = []
        for agent in self.agents.values():
            if capability in agent.capabilities:
                matching_agents.append(agent)
        return matching_agents
    
    async def execute_agent(
        self,
        agent_name: str,
        agent_input: AgentInput
    ) -> AgentOutput:
        """Execute a specific agent with given input."""
        agent = self.get_agent(agent_name)
        
        logger.info(
            "Executing agent",
            agent_name=agent_name,
            task_id=str(agent_input.task_id)
        )
        
        return await agent.execute(agent_input)


# Global agent registry instance
agent_registry = AgentRegistry()
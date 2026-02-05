"""
Test Suite for AI Orchestration Platform
"""
import pytest
import asyncio
from uuid import uuid4
from src.models.core import (
    OrchestratorRequest,
    AgentInput,
    TaskType,
    EntityType,
    InsightType
)
from src.orchestrator.orchestrator import orchestrator
from src.agents.search_agent import search_agent
from src.agents.memory_agent import memory_agent
from src.core.llm_client import llm_client


class TestOrchestrator:
    """Test orchestrator functionality."""
    
    @pytest.mark.asyncio
    async def test_process_simple_request(self):
        """Test processing a simple search request."""
        request = OrchestratorRequest(
            user_query="Find information about sustainable construction practices"
        )
        
        response = await orchestrator.process_request(request)
        
        assert response.request_id == request.request_id
        assert response.confidence > 0.0
        assert len(response.agent_outputs) > 0
    
    @pytest.mark.asyncio
    async def test_intent_classification(self):
        """Test LLM intent classification."""
        query = "I need to analyze a contract for compliance issues"
        
        intent = await orchestrator._classify_intent(query)
        
        assert "intent" in intent
        assert "entities" in intent
        assert "required_tasks" in intent
        assert "domain" in intent
    
    def test_task_decomposition(self):
        """Test task decomposition logic."""
        intent_analysis = {
            "intent": "find vendors",
            "entities": ["construction", "vendors"],
            "required_tasks": ["search", "risk"],
            "domain": "real_estate"
        }
        
        request = OrchestratorRequest(
            user_query="Find construction vendors"
        )
        
        tasks = orchestrator._decompose_into_tasks(intent_analysis, request)
        
        assert len(tasks) > 0
        assert all("task_type" in task for task in tasks)


class TestSearchAgent:
    """Test search agent functionality."""
    
    @pytest.mark.asyncio
    async def test_search_execution(self):
        """Test search agent execution."""
        agent_input = AgentInput(
            task_type=TaskType.SEARCH,
            context={"search_query": "sustainable building materials"},
            instructions="Search for sustainable building materials"
        )
        
        output = await search_agent.execute(agent_input)
        
        assert output.agent_name == "search_agent"
        assert output.confidence >= 0.0
        assert isinstance(output.result, dict)
    
    def test_search_query_extraction(self):
        """Test search query extraction."""
        agent_input = AgentInput(
            task_type=TaskType.SEARCH,
            context={"search_query": "test query"},
            instructions="Perform search"
        )
        
        query = search_agent._extract_search_query(agent_input)
        
        assert query == "test query"


class TestMemoryAgent:
    """Test memory agent functionality."""
    
    @pytest.mark.asyncio
    async def test_memory_storage(self):
        """Test storing memory entry."""
        agent_input = AgentInput(
            task_type=TaskType.MEMORY_STORAGE,
            context={
                "memory_entry": {
                    "entity_type": "vendor",
                    "entity_name": "Test Vendor",
                    "insight_type": "vendor_reputation",
                    "content": {"rating": 4.5},
                    "confidence_score": 0.85,
                    "source_agent": "test_agent",
                    "tags": ["test"]
                }
            },
            instructions="Store memory"
        )
        
        output = await memory_agent.execute(agent_input)
        
        assert output.agent_name == "memory_agent"
        assert output.confidence > 0.0
        assert "operation" in output.result
    
    @pytest.mark.asyncio
    async def test_memory_retrieval(self):
        """Test retrieving memory entries."""
        agent_input = AgentInput(
            task_type=TaskType.MEMORY_RETRIEVAL,
            context={
                "entity_type": "vendor",
                "entity_name": "Test Vendor"
            },
            instructions="Retrieve memory"
        )
        
        output = await memory_agent.execute(agent_input)
        
        assert output.agent_name == "memory_agent"
        assert "memories" in output.result


class TestLLMClient:
    """Test LLM client functionality."""
    
    @pytest.mark.asyncio
    async def test_generate(self):
        """Test basic LLM generation."""
        prompt = "What is 2+2? Answer briefly."
        
        response = await llm_client.generate(prompt, temperature=0.1)
        
        assert isinstance(response, str)
        assert len(response) > 0
    
    @pytest.mark.asyncio
    async def test_classify_intent(self):
        """Test intent classification."""
        query = "Find vendors for construction project"
        
        result = await llm_client.classify_intent(query)
        
        assert isinstance(result, dict)
        assert "intent" in result


class TestIntegration:
    """Integration tests for end-to-end flows."""
    
    @pytest.mark.asyncio
    async def test_full_orchestration_flow(self):
        """Test complete orchestration from request to response."""
        request = OrchestratorRequest(
            user_query="What are the top 3 sustainable construction trends?",
            domain_context={"domain": "construction"}
        )
        
        response = await orchestrator.process_request(request)
        
        # Validate response structure
        assert response.request_id == request.request_id
        assert isinstance(response.response, dict)
        assert "answer" in response.response
        assert len(response.agent_outputs) > 0
        assert response.confidence >= 0.0
        assert response.execution_time_ms > 0
    
    @pytest.mark.asyncio
    async def test_parallel_agent_execution(self):
        """Test parallel execution of multiple agents."""
        agent_inputs = [
            AgentInput(
                task_type=TaskType.SEARCH,
                context={},
                instructions=f"Search query {i}"
            )
            for i in range(3)
        ]
        
        outputs = await orchestrator._execute_agents_parallel(agent_inputs)
        
        assert len(outputs) > 0


# Pytest configuration
@pytest.fixture(scope="session")
def event_loop():
    """Create event loop for async tests."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
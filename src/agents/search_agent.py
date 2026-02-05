from datetime import datetime
import httpx
from config.settings import settings
from src.utils.logging import get_logger
from src.models.core import AgentInput, AgentOutput

logger = get_logger(__name__)


class SearchAgent:
    """
    Search agent that delegates execution to Agentic Research Service.
    """

    name = "search_agent"
    capabilities = [
        "web_search",
        "vendor_discovery",
        "regulation_lookup",
        "market_data_retrieval",
        "benchmark_discovery"
    ]

    def __init__(self):
        self.base_url = settings.RESEARCH_SERVICE_URL
        self.timeout = settings.RESEARCH_SERVICE_TIMEOUT

    async def execute(self, agent_input: AgentInput) -> AgentOutput:
        start_time = datetime.utcnow()

        query = agent_input.context.get(
            "original_query",
            agent_input.instructions
        )

        session_id = str(agent_input.task_id)

        logger.info(
            "Delegating search to research service",
            query=query,
            session_id=session_id
        )

        try:
            async with httpx.AsyncClient(timeout=None) as client:
                response = await client.post(
                    f"{self.base_url}/research",
                    json={
                        "topic": query,
                        "channel_id": session_id
                    }
                )

                response.raise_for_status()
                data = response.json()

            execution_time = (datetime.utcnow() - start_time).total_seconds() * 1000

            return AgentOutput(
                task_id=agent_input.task_id,
                agent_name=self.name,
                result={
                    "summary": data.get("result"),
                    "provider": "agentic_research_service"
                },
                confidence=0.85,  # research agent already reasons deeply
                sources=[],       # sources embedded inside result
                execution_time_ms=execution_time,
                metadata={
                    "service": "research-service",
                    "mode": "delegated"
                }
            )

        except Exception as e:
            logger.error(
                "Search delegation failed",
                error=str(e)
            )

            return AgentOutput(
                task_id=agent_input.task_id,
                agent_name=self.name,
                result={},
                confidence=0.0,
                errors=[str(e)],
                execution_time_ms=(datetime.utcnow() - start_time).total_seconds() * 1000
            )


search_agent = SearchAgent()

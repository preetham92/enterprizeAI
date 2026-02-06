from fastapi import APIRouter
from src.agents.memory_agent import memory_agent
from src.models.core import AgentInput, AgentOutput

router = APIRouter(prefix="/memory", tags=["Memory"])

@router.post("/ingest", response_model=AgentOutput)
async def ingest_memory(agent_input: AgentInput):
    """
    Direct memory ingestion endpoint (DEBUG / TEST ONLY).
    Bypasses orchestrator and stores memory directly.
    """
    return await memory_agent.execute(agent_input)

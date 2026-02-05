"""
Orchestrator - Central control plane for multi-agent system.
Interprets intent, routes tasks, coordinates agents, synthesizes responses.
File: src/orchestrator.py
"""

from typing import List, Dict, Any, Optional
from uuid import UUID
import asyncio
from datetime import datetime

from config.settings import settings
from src.utils.logging import get_logger
from src.models.core import (
    OrchestratorRequest,
    OrchestratorResponse,
    AgentInput,
    AgentOutput,
    TaskType
)

from src.core.llm_client import llm_client
from src.agents.registry import agent_registry
from src.agents.memory_agent import memory_agent

logger = get_logger(__name__)


class Orchestrator:
    """
    Central Orchestrator - Controls all agent execution and workflow.
    """

    def __init__(self):
        self.max_parallel_agents = getattr(settings, "max_parallel_agents", 5)
        self.agent_registry = agent_registry

    # ------------------------------------------------------------------
    # MAIN ENTRYPOINT
    # ------------------------------------------------------------------

    async def process_request(
        self,
        request: OrchestratorRequest
    ) -> OrchestratorResponse:
        start_time = datetime.utcnow()

        logger.info(
            "Orchestrator processing request",
            request_id=str(request.request_id),
            query_length=len(request.user_query)
        )

        try:
            # 1️⃣ Intent classification
            intent_analysis = await self._classify_intent(request.user_query)

            logger.info(
                "Intent classified",
                request_id=str(request.request_id),
                intent=intent_analysis.get("intent"),
                domain=intent_analysis.get("domain")
            )

            # 2️⃣ Task decomposition
            tasks = self._decompose_into_tasks(intent_analysis, request)

            logger.info(
                "Tasks decomposed",
                request_id=str(request.request_id),
                task_count=len(tasks)
            )

            # 3️⃣ Memory retrieval (ASYNC – FIXED)
            memory_context = await self._retrieve_memory_context(
                intent_analysis,
                request
            )

            # 4️⃣ Create agent inputs
            agent_inputs = self._create_agent_inputs(
                tasks,
                memory_context,
                request
            )

            # 5️⃣ Execute agents
            agent_outputs = await self._execute_agents_parallel(agent_inputs)

            logger.info(
                "Agents executed",
                request_id=str(request.request_id),
                successful_agents=len([o for o in agent_outputs if not o.errors])
            )

            # 6️⃣ Validate outputs
            validated_outputs = self._validate_outputs(agent_outputs)

            # 7️⃣ Synthesize response
            final_response = await self._synthesize_response(
                request.user_query,
                validated_outputs,
                memory_context
            )

            # 8️⃣ Persist learnings
            await self._persist_learnings(
                validated_outputs,
                intent_analysis,
                request.request_id
            )

            # Metrics
            overall_confidence = self._calculate_overall_confidence(validated_outputs)

            all_sources = list(
                {src for out in validated_outputs for src in out.sources}
            )

            all_errors = [err for out in agent_outputs for err in out.errors]

            execution_time = (
                datetime.utcnow() - start_time
            ).total_seconds() * 1000

            logger.info(
                "Orchestrator completed",
                request_id=str(request.request_id),
                execution_time_ms=execution_time,
                confidence=overall_confidence
            )

            return OrchestratorResponse(
                request_id=request.request_id,
                response=final_response,
                agent_outputs=validated_outputs,
                confidence=overall_confidence,
                sources=all_sources,
                execution_time_ms=execution_time,
                errors=all_errors,
                metadata={
                    "intent": intent_analysis.get("intent"),
                    "domain": intent_analysis.get("domain"),
                    "task_count": len(tasks),
                    "memory_items_used": len(memory_context) if memory_context else 0
                }
            )

        except Exception as e:
            logger.exception(
                "Orchestrator failed",
                request_id=str(request.request_id)
            )

            execution_time = (
                datetime.utcnow() - start_time
            ).total_seconds() * 1000

            return OrchestratorResponse(
                request_id=request.request_id,
                response={"error": "Failed to process request", "details": str(e)},
                agent_outputs=[],
                confidence=0.0,
                sources=[],
                execution_time_ms=execution_time,
                errors=[str(e)]
            )

    # ------------------------------------------------------------------
    # INTERNAL STEPS
    # ------------------------------------------------------------------

    async def _classify_intent(self, user_query: str) -> Dict[str, Any]:
        return await llm_client.classify_intent(user_query)

    def _decompose_into_tasks(
        self,
        intent_analysis: Dict[str, Any],
        request: OrchestratorRequest
    ) -> List[Dict[str, Any]]:
        tasks = []
        required_tasks = intent_analysis.get("required_tasks", [])

        task_mapping = {
            "search": TaskType.SEARCH,
            "web": TaskType.SEARCH,
            "find": TaskType.SEARCH,
            "document": TaskType.DOCUMENT_ANALYSIS,
            "contract": TaskType.DOCUMENT_ANALYSIS,
            "risk": TaskType.RISK_COMPLIANCE,
            "compliance": TaskType.RISK_COMPLIANCE,
            "negotiate": TaskType.NEGOTIATION_STRATEGY,
            "forecast": TaskType.ANALYTICS_FORECAST,
            "analytics": TaskType.ANALYTICS_FORECAST,
            "predict": TaskType.ANALYTICS_FORECAST,
            "fraud": TaskType.FRAUD_DETECTION,
            "anomaly": TaskType.FRAUD_DETECTION
        }

        for task_desc in required_tasks:
            desc = task_desc.lower()
            for key, task_type in task_mapping.items():
                if key in desc:
                    tasks.append({
                        "task_type": task_type,
                        "description": task_desc,
                        "context": intent_analysis
                    })
                    break

        if request.document_text:
            if not any(t["task_type"] == TaskType.DOCUMENT_ANALYSIS for t in tasks):
                tasks.append({
                    "task_type": TaskType.DOCUMENT_ANALYSIS,
                    "description": "Analyze provided document text",
                    "context": {"priority": "high"}
                })

        if not tasks:
            tasks.append({
                "task_type": TaskType.SEARCH,
                "description": "Perform web search",
                "context": intent_analysis
            })

        return tasks

    async def _retrieve_memory_context(
        self,
        intent_analysis: Dict[str, Any],
        request: OrchestratorRequest
    ) -> Optional[List[Dict[str, Any]]]:
        entities = intent_analysis.get("entities", [])
        if not entities:
            return None

        try:
            entity_name = entities[0]
            memory_context = await memory_agent.retrieve_context_for_entity(
                entity_type="generic",
                entity_name=entity_name,
                limit=5
            )
            return memory_context or None

        except Exception as e:
            logger.warning("Memory retrieval failed", error=str(e))
            return None

    def _create_agent_inputs(
        self,
        tasks: List[Dict[str, Any]],
        memory_context: Optional[List[Dict[str, Any]]],
        request: OrchestratorRequest
    ) -> List[AgentInput]:
        agent_inputs = []

        for task in tasks:
            agent_inputs.append(
                AgentInput(
                    task_type=task["task_type"],
                    context={
                        **task.get("context", {}),
                        **(request.domain_context or {}),
                        "document_text": request.document_text,
                        "original_query": request.user_query
                    },
                    memory_context=memory_context,
                    instructions=task.get("description", request.user_query)
                )
            )

        return agent_inputs

    async def _execute_agents_parallel(
        self,
        agent_inputs: List[AgentInput]
    ) -> List[AgentOutput]:
        grouped: Dict[TaskType, List[AgentInput]] = {}
        for ai in agent_inputs:
            grouped.setdefault(ai.task_type, []).append(ai)

        all_outputs: List[AgentOutput] = []

        for task_type, inputs in grouped.items():
            agents = self.agent_registry.get_agents_for_task(task_type)
            if not agents:
                logger.warning("No agent found", task_type=task_type.value)
                continue

            agent = agents[0]

            for i in range(0, len(inputs), self.max_parallel_agents):
                batch = inputs[i:i + self.max_parallel_agents]

                try:
                    results = await asyncio.wait_for(
                        asyncio.gather(
                            *(agent.execute(ai) for ai in batch),
                            return_exceptions=True
                        ),
                        timeout=settings.agent_execution_timeout
                    )

                    for res in results:
                        if isinstance(res, Exception):
                            logger.error("Agent execution error", error=str(res))
                        else:
                            all_outputs.append(res)

                except asyncio.TimeoutError:
                    logger.error("Agent execution timed out", agent=agent.name)

                    # 🔁 Graceful fallback
                    for ai in batch:
                        all_outputs.append(
                            AgentOutput(
                                task_id=ai.task_id,
                                agent_name=agent.name,
                                result={
                                    "message": "Agent execution timed out",
                                    "task_type": ai.task_type
                                },
                                confidence=0.3,
                                errors=["timeout"]
                            )
                        )

        return all_outputs

    def _validate_outputs(
        self,
        agent_outputs: List[AgentOutput]
    ) -> List[AgentOutput]:
        return [
            o for o in agent_outputs
            if not (o.errors and o.confidence < 0.3)
        ]

    async def _synthesize_response(
        self,
        query: str,
        agent_outputs: List[AgentOutput],
        memory_context: Optional[List[Dict[str, Any]]]
    ) -> Dict[str, Any]:
        if not agent_outputs:
            return {
                "answer": "Unable to process request. No valid agent outputs."
            }

        synthesis = await llm_client.synthesize_response(
            query,
            agent_outputs,
            memory_context
        )

        return {
            "answer": synthesis,
            "agent_contributions": [
                {
                    "agent": o.agent_name,
                    "confidence": o.confidence,
                    "summary": (
                        str(o.result)[:200] + "..."
                        if len(str(o.result)) > 200
                        else str(o.result)
                    )
                }
                for o in agent_outputs
            ]
        }

    async def _persist_learnings(
        self,
        agent_outputs: List[AgentOutput],
        intent_analysis: Dict[str, Any],
        request_id: UUID
    ) -> None:
        high_conf = [
            o for o in agent_outputs
            if o.confidence >= settings.memory_confidence_threshold
            and not o.errors
        ]

        if not high_conf:
            return

        entity = (
            intent_analysis.get("entities", ["Unknown"])[0]
        )

        for o in high_conf:
            await memory_agent.execute(
                AgentInput(
                    task_type=TaskType.MEMORY_STORAGE,
                    context={
                        "memory_entry": {
                            "entity_type": "generic",
                            "entity_name": entity,
                            "insight_type": "generic_learning",
                            "content": {
                                "result": o.result,
                                "sources": o.sources
                            },
                            "confidence_score": o.confidence,
                            "source_agent": o.agent_name,
                            "tags": [intent_analysis.get("domain", "generic")]
                        }
                    },
                    instructions="Store learning"
                )
            )

    def _calculate_overall_confidence(
        self,
        agent_outputs: List[AgentOutput]
    ) -> float:
        if not agent_outputs:
            return 0.0
        return round(
            sum(o.confidence for o in agent_outputs) / len(agent_outputs),
            2
        )


# Global orchestrator instance
orchestrator = Orchestrator()

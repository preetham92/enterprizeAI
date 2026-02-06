"""
Memory Agent - PostgreSQL-backed memory and learning system.
ONLY agent that interacts with the database.
"""
from typing import List, Dict, Any, Optional
from datetime import datetime
from uuid import UUID
from sqlalchemy import and_, or_, desc
from sqlalchemy.exc import SQLAlchemyError
from config.settings import settings
from src.utils.logging import get_logger
from src.models.core import AgentInput, AgentOutput, MemoryEntry, EntityType, InsightType
from src.memory.database import db_manager, MemoryEntryModel

logger = get_logger(__name__)


class MemoryAgent:
    """
    Memory Agent - Manages PostgreSQL-backed memory layer.
    Retrieves historical context and stores validated learnings.
    """
    
    name = "memory_agent"
    capabilities = [
        "memory_retrieval",
        "memory_storage",
        "historical_context",
        "learning_persistence"
    ]
    
    def __init__(self):
        self.confidence_threshold = settings.memory_confidence_threshold
        self.max_results = settings.memory_max_results
        self.relevance_threshold = settings.memory_relevance_threshold
    
    async def execute(self, agent_input: AgentInput) -> AgentOutput:
        """
        Execute memory operation (retrieval or storage).
        
        Args:
            agent_input: Memory task input
            
        Returns:
            AgentOutput with memory operation result
        """
        start_time = datetime.utcnow()
        
        logger.info(
            "Memory agent executing",
            task_id=str(agent_input.task_id),
            task_type=agent_input.task_type
        )
        
        try:
            if agent_input.task_type == "memory_retrieval":
                result = await self._retrieve_memory(agent_input)
            elif agent_input.task_type == "memory_storage":
                result = await self._store_memory(agent_input)
            else:
                raise ValueError(f"Unsupported memory task type: {agent_input.task_type}")
            
            execution_time = (datetime.utcnow() - start_time).total_seconds() * 1000
            
            logger.info(
                "Memory agent completed",
                task_id=str(agent_input.task_id),
                operation=agent_input.task_type
            )
            
            return AgentOutput(
                task_id=agent_input.task_id,
                agent_name=self.name,
                result=result,
                confidence=0.9,  # High confidence in database operations
                execution_time_ms=execution_time
            )
            
        except Exception as e:
            logger.error(
                "Memory agent failed",
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
    
    async def _retrieve_memory(self, agent_input: AgentInput) -> Dict[str, Any]:
        """Retrieve relevant memories from PostgreSQL."""
        context = agent_input.context
        
        entity_type = context.get("entity_type")
        entity_name = context.get("entity_name")
        insight_types = context.get("insight_types", [])
        
        logger.info(
            "Retrieving memory",
            entity_type=entity_type,
            entity_name=entity_name,
            insight_types=insight_types
        )
        
        session = db_manager.get_session()
        
        try:
            # Build query
            query = session.query(MemoryEntryModel)
            
            # Filter by entity if specified
            if entity_type and entity_name:
                query = query.filter(
                    and_(
                        MemoryEntryModel.entity_type == entity_type,
                        MemoryEntryModel.entity_name == entity_name
                    )
                )
            elif entity_type:
                query = query.filter(MemoryEntryModel.entity_type == entity_type)
            elif entity_name:
                query = query.filter(MemoryEntryModel.entity_name == entity_name)
            
            # Filter by insight types if specified
            if insight_types:
                query = query.filter(MemoryEntryModel.insight_type.in_(insight_types))
            
            # Filter by confidence threshold
            query = query.filter(
                MemoryEntryModel.confidence_score >= self.confidence_threshold
            )
            
            # Order by confidence and recency
            query = query.order_by(
                desc(MemoryEntryModel.confidence_score),
                desc(MemoryEntryModel.updated_at)
            )
            
            # Limit results
            query = query.limit(self.max_results)
            
            # Execute query
            memories = query.all()
            
            # Convert to dictionaries
            results = []
            for memory in memories:
                results.append({
                    "id": str(memory.id),
                    "entity_type": memory.entity_type,
                    "entity_name": memory.entity_name,
                    "insight_type": memory.insight_type,
                    "content": memory.content,
                    "confidence_score": memory.confidence_score,
                    "source_agent": memory.source_agent,
                    "tags": memory.tags,
                    "created_at": memory.created_at.isoformat(),
                    "updated_at": memory.updated_at.isoformat()
                })
            
            logger.info(
                "Memory retrieval complete",
                results_count=len(results)
            )
            
            return {
                "memories": results,
                "count": len(results),
                "query_params": {
                    "entity_type": entity_type,
                    "entity_name": entity_name,
                    "insight_types": insight_types
                }
            }
            
        except SQLAlchemyError as e:
            logger.error("Database error during memory retrieval", error=str(e))
            raise
        finally:
            session.close()
    
    async def _store_memory(self, agent_input: AgentInput) -> Dict[str, Any]:
        """Store new learning in PostgreSQL."""
        context = agent_input.context
        
        # Extract memory entry data
        memory_data = context.get("memory_entry")
        if not memory_data:
            raise ValueError("No memory_entry in context")
        
        logger.info(
            "Storing memory",
            entity_type=memory_data.get("entity_type"),
            entity_name=memory_data.get("entity_name"),
            insight_type=memory_data.get("insight_type")
        )
        
        session = db_manager.get_session()
        
        try:
            # Check if similar memory already exists
            existing = session.query(MemoryEntryModel).filter(
                and_(
                    MemoryEntryModel.entity_type == memory_data["entity_type"],
                    MemoryEntryModel.entity_name == memory_data["entity_name"],
                    MemoryEntryModel.insight_type == memory_data["insight_type"]
                )
            ).first()
            
            if existing:
                # Update existing memory
                existing.content = memory_data["content"]
                existing.confidence_score = max(
                    existing.confidence_score,
                    memory_data["confidence_score"]
                )
                existing.source_agent = memory_data["source_agent"]
                existing.tags = list(set(existing.tags + memory_data.get("tags", [])))
                existing.updated_at = datetime.utcnow()
                
                session.commit()
                
                logger.info("Updated existing memory", memory_id=str(existing.id))
                
                return {
                    "operation": "updated",
                    "memory_id": str(existing.id),
                    "entity_type": existing.entity_type,
                    "entity_name": existing.entity_name
                }
            else:
                # Create new memory entry
                new_memory = MemoryEntryModel(
                    entity_type=memory_data["entity_type"],
                    entity_name=memory_data["entity_name"],
                    insight_type=memory_data["insight_type"],
                    content=memory_data["content"],
                    confidence_score=memory_data["confidence_score"],
                    source_agent=memory_data["source_agent"],
                    tags=memory_data.get("tags", [])
                )
                
                session.add(new_memory)
                session.commit()
                
                logger.info("Stored new memory", memory_id=str(new_memory.id))
                
                return {
                    "operation": "created",
                    "memory_id": str(new_memory.id),
                    "entity_type": new_memory.entity_type,
                    "entity_name": new_memory.entity_name
                }
        
        except SQLAlchemyError as e:
            session.rollback()
            logger.error("Database error during memory storage", error=str(e))
            raise
        finally:
            session.close()
    
    def retrieve_context_for_entity(
        self,
        entity_type: str,
        entity_name: str,
        limit: int = 5
    ) -> List[Dict[str, Any]]:
        """
        Synchronous method to retrieve memory context for an entity.
        Used by orchestrator to inject context into agent prompts.
        """
        session = db_manager.get_session()
        
        try:
            memories = session.query(MemoryEntryModel).filter(
                and_(
                    MemoryEntryModel.entity_type == entity_type,
                    MemoryEntryModel.entity_name == entity_name,
                    MemoryEntryModel.confidence_score >= self.confidence_threshold
                )
            ).order_by(
                desc(MemoryEntryModel.confidence_score)
            ).limit(limit).all()
            
            return [
                {
                    "insight_type": m.insight_type,
                    "content": m.content,
                    "confidence": m.confidence_score,
                    "source": m.source_agent
                }
                for m in memories
            ]
        
        finally:
            session.close()


# Global memory agent instance
memory_agent = MemoryAgent()
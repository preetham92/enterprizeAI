"""
Core data models for the AI Orchestration Platform.
Defines all interfaces and contracts between components.
File: src/models/core.py
"""
from typing import Any, Dict, List, Optional, Union
from datetime import datetime
from enum import Enum
from uuid import UUID, uuid4
from pydantic import BaseModel, Field, field_validator, model_validator


class TaskType(str, Enum):
    """Types of tasks that can be executed."""
    SEARCH = "search"
    DOCUMENT_ANALYSIS = "document_analysis"
    RISK_COMPLIANCE = "risk_compliance"
    NEGOTIATION_STRATEGY = "negotiation_strategy"
    ANALYTICS_FORECAST = "analytics_forecast"
    FRAUD_DETECTION = "fraud_detection"
    MEMORY_RETRIEVAL = "memory_retrieval"
    MEMORY_STORAGE = "memory_storage"


class EntityType(str, Enum):
    """Types of entities in the system."""
    VENDOR = "vendor"
    CONTRACT = "contract"
    INVOICE = "invoice"
    PURCHASE_ORDER = "purchase_order"
    REGULATION = "regulation"
    MARKET_DATA = "market_data"
    GENERIC = "generic"


class InsightType(str, Enum):
    """Types of insights stored in memory."""
    VENDOR_REPUTATION = "vendor_reputation"
    CONTRACT_PATTERN = "contract_pattern"
    RISK_INDICATOR = "risk_indicator"
    NEGOTIATION_OUTCOME = "negotiation_outcome"
    FRAUD_PATTERN = "fraud_pattern"
    MARKET_TREND = "market_trend"
    PERFORMANCE_METRIC = "performance_metric"
    GENERIC_LEARNING = "generic_learning"


class AgentInput(BaseModel):
    """Standard input structure for all agents."""
    task_id: UUID = Field(default_factory=uuid4)
    task_type: TaskType
    context: Dict[str, Any] = Field(
        default_factory=dict,
        description="Domain context, entity info, constraints, document_text"
    )
    memory_context: Optional[List[Dict[str, Any]]] = Field(
        default=None,
        description="Historical context from memory"
    )
    instructions: str = Field(
        description="Specific instructions for the agent"
    )
    
    class Config:
        use_enum_values = True


class AgentOutput(BaseModel):
    """Standard output structure for all agents."""
    task_id: UUID
    agent_name: str
    result: Union[str, Dict[str, Any], List[Any]] = Field(
        description="Agent execution result"
    )
    confidence: float = Field(
        ge=0.0, le=1.0,
        description="Confidence score 0.0 to 1.0"
    )
    sources: List[str] = Field(
        default_factory=list,
        description="URLs or references supporting the result"
    )
    errors: List[str] = Field(
        default_factory=list,
        description="Any errors encountered during execution"
    )
    execution_time_ms: Optional[float] = None
    metadata: Dict[str, Any] = Field(default_factory=dict)
    
    @field_validator('confidence')
    @classmethod
    def validate_confidence(cls, v: float) -> float:
        """Ensure confidence is between 0 and 1."""
        return max(0.0, min(1.0, v))


class SearchResult(BaseModel):
    """Result from web search."""
    url: str
    title: str
    snippet: str
    relevance_score: float = Field(ge=0.0, le=1.0)
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    metadata: Dict[str, Any] = Field(default_factory=dict)


class MemoryEntry(BaseModel):
    """Memory entry structure."""
    id: Optional[UUID] = None
    entity_type: EntityType
    entity_name: str
    insight_type: InsightType
    content: Dict[str, Any]
    confidence_score: float = Field(ge=0.0, le=1.0)
    source_agent: str
    tags: List[str] = Field(default_factory=list)
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    
    class Config:
        use_enum_values = True


class OrchestratorRequest(BaseModel):
    """Request to the orchestrator."""
    request_id: UUID = Field(default_factory=uuid4)
    user_query: str = Field(
        min_length=1,
        description="User's natural language query"
    )
    
    # Optional top-level field for document text
    document_text: Optional[str] = Field(
        default=None,
        description="Raw text content to be analyzed (contracts, emails, logs)"
    )
    
    domain_context: Optional[Dict[str, Any]] = Field(
        default=None,
        description="Optional domain-specific context"
    )
    constraints: Optional[Dict[str, Any]] = Field(
        default=None,
        description="Execution constraints"
    )
    
    @field_validator('user_query')
    @classmethod
    def sanitize_query(cls, v: str) -> str:
        """Basic sanitization of user query."""
        return v.strip()[:5000]  # Limit length

    # --- CRITICAL FIX FOR 422 ERRORS ---
    @model_validator(mode='before')
    @classmethod
    def normalize_document_text(cls, data: Any) -> Any:
        """
        Pre-validator to fix structure mismatches.
        If 'document_text' is buried inside 'constraints', move it to the top level.
        """
        if isinstance(data, dict):
            # Check if document_text is missing at top level but present in constraints
            if not data.get('document_text'):
                constraints = data.get('constraints')
                if isinstance(constraints, dict) and 'document_text' in constraints:
                    # Move it up
                    data['document_text'] = constraints['document_text']
        return data
    # -----------------------------------


class OrchestratorResponse(BaseModel):
    """Response from the orchestrator."""
    request_id: UUID
    response: Dict[str, Any] = Field(
        description="Structured response to user query"
    )
    agent_outputs: List[AgentOutput] = Field(
        description="Individual agent outputs"
    )
    confidence: float = Field(
        ge=0.0, le=1.0,
        description="Overall confidence in response"
    )
    sources: List[str] = Field(
        description="All sources used in generating response"
    )
    execution_time_ms: float
    errors: List[str] = Field(default_factory=list)
    metadata: Dict[str, Any] = Field(default_factory=dict)


class LLMRequest(BaseModel):
    """Request to the LLM (Ollama)."""
    prompt: str
    model: str = "qwen3:8b"
    stream: bool = True
    options: Optional[Dict[str, Any]] = None


class LLMResponse(BaseModel):
    """Response from the LLM."""
    text: str
    done: bool
    total_duration: Optional[int] = None
    load_duration: Optional[int] = None
    prompt_eval_count: Optional[int] = None
    eval_count: Optional[int] = None
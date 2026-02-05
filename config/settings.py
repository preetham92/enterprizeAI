from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field, field_validator


class Settings(BaseSettings):
    

    # --------------------
    # Search (legacy / internal)
    # --------------------
    TAVILY_API_KEY: str

    search_timeout: int = Field(default=30, ge=5, le=120)
    search_max_results: int = Field(default=10, ge=1, le=50)
    search_user_agent: str = Field(
        default="Mozilla/5.0 (AI-Orchestration-Platform/1.0)"
    )

    # --------------------
    # External Research Service (NEW)
    # --------------------
    RESEARCH_SERVICE_URL: str = Field(
        default="http://research_service:8000",
        description="Agentic Research Service base URL"
    )

    RESEARCH_SERVICE_TIMEOUT: int = Field(
        default=600,
        ge=60,
        le=1800,
        description="Timeout for delegated research execution (seconds)"
    )

    # --------------------
    # Database
    # --------------------
    database_url: str = Field(
        description="PostgreSQL connection string"
    )
    db_pool_size: int = Field(default=20, ge=1, le=100)
    db_max_overflow: int = Field(default=10, ge=0, le=50)
    db_pool_timeout: int = Field(default=30, ge=5, le=300)

    # --------------------
    # Ollama LLM
    # --------------------
    ollama_base_url: str = Field(
        default="https://dev.assisto.tech/ollama",
        description="Ollama API base URL"
    )
    ollama_model: str = Field(default="qwen3:8b")
    ollama_timeout: int = Field(default=120, ge=10, le=600)
    ollama_max_retries: int = Field(default=3, ge=1, le=10)

    # --------------------
    # System
    # --------------------
    environment: str = Field(default="production")
    log_level: str = Field(default="INFO")
    max_parallel_agents: int = Field(default=5, ge=1, le=20)
    agent_execution_timeout: int = Field(default=180, ge=10, le=300)
    orchestrator_timeout: int = Field(default=300, ge=60, le=1800)

    # --------------------
    # Security
    # --------------------
    api_key_header: str = Field(default="X-API-Key")
    rate_limit_requests: int = Field(default=100, ge=1, le=10000)
    rate_limit_window: int = Field(default=60, ge=1, le=3600)

    # --------------------
    # Memory
    # --------------------
    memory_confidence_threshold: float = Field(default=0.7, ge=0.0, le=1.0)
    memory_max_results: int = Field(default=10, ge=1, le=100)
    memory_relevance_threshold: float = Field(default=0.6, ge=0.0, le=1.0)

    # --------------------
    # Validators
    # --------------------
    @field_validator("log_level")
    @classmethod
    def validate_log_level(cls, v: str) -> str:
        valid = {"DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"}
        v = v.upper()
        if v not in valid:
            raise ValueError(f"log_level must be one of {valid}")
        return v

    @field_validator("environment")
    @classmethod
    def validate_environment(cls, v: str) -> str:
        valid = {"development", "staging", "production"}
        v = v.lower()
        if v not in valid:
            raise ValueError(f"environment must be one of {valid}")
        return v

    model_config = SettingsConfigDict(
        env_file=".env",
        case_sensitive=False,
        extra="forbid"
    )


settings = Settings()

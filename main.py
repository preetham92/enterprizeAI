"""
FastAPI Application - REST API interface for the AI Orchestration Platform.
"""

import time
from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from sqlalchemy import text

from config.settings import settings
from src.utils.logging import get_logger
from src.memory.database import db_manager
from src.models.core import OrchestratorRequest, OrchestratorResponse
from src.orchestrator.orchestrator import orchestrator
from src.api.routes.memory import router as memory_router
from fastapi import FastAPI





logger = get_logger(__name__)


# ============================================================
# Lifespan
# ============================================================

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Startup / shutdown lifecycle."""
    logger.info("Starting AI Orchestration Platform")

    try:
        db_manager.initialize()
        logger.info("Database initialized")
        yield
    finally:
        logger.info("Shutting down AI Orchestration Platform")
        db_manager.close()


# ============================================================
# App
# ============================================================

app = FastAPI(
    title="AI Orchestration Platform",
    description="Multi-agent AI system with live web search and PostgreSQL memory",
    version="1.0.0",
    lifespan=lifespan,
)
app.include_router(memory_router)

# ============================================================
# Middleware
# ============================================================

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # tighten in prod
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.middleware("http")
async def log_requests(request: Request, call_next):
    start_time = time.time()
    response = await call_next(request)
    duration_ms = round((time.time() - start_time) * 1000, 2)

    logger.info(
        "HTTP request",
        method=request.method,
        path=request.url.path,
        status_code=response.status_code,
        duration_ms=duration_ms,
    )
    return response


# ============================================================
# Error Handling
# ============================================================

@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    logger.error(
        "Unhandled exception",
        path=request.url.path,
        error=str(exc),
        exc_info=True,
    )

    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "error": "Internal server error",
            "message": str(exc)
            if settings.environment == "development"
            else "An error occurred",
        },
    )


# ============================================================
# Routes
# ============================================================

@app.get("/")
async def root():
    return {
        "service": "AI Orchestration Platform",
        "version": "1.0.0",
        "status": "running",
        "environment": settings.environment,
    }


@app.get("/health")
async def health_check():
    """Health check endpoint (contract-stable)."""
    try:
        session = db_manager.get_session()
        session.execute(text("SELECT 1"))
        session.close()

        return {
            "status": "healthy",
            "database": "connected",
            "timestamp": time.time(),
        }

    except Exception as e:
        logger.error("Health check failed", error=str(e))
        return {
            "status": "unhealthy",
            "database": "disconnected",
            "error": str(e),
            "timestamp": time.time(),
        }


@app.post("/orchestrate", response_model=OrchestratorResponse)
async def orchestrate_request(request: OrchestratorRequest):
    """Main orchestration endpoint."""
    try:
        logger.info(
            "Received orchestration request",
            request_id=str(request.request_id),
            query_length=len(request.user_query),
        )

        return await orchestrator.process_request(request)

    except Exception as e:
        logger.error(
            "Orchestration failed",
            request_id=str(request.request_id),
            error=str(e),
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Orchestration failed",
        )


@app.get("/agents")
async def list_agents():
    from src.agents.registry import agent_registry

    return {
        "agents": agent_registry.list_all_agents(),
        "count": len(agent_registry.agents),
    }


@app.get("/memory/stats")
async def memory_statistics():
    from src.memory.database import MemoryEntryModel

    try:
        session = db_manager.get_session()

        total_entries = session.query(MemoryEntryModel).count()
        entity_types = (
            session.query(MemoryEntryModel.entity_type)
            .distinct()
            .all()
        )

        session.close()

        return {
            "total_entries": total_entries,
            "entity_types": [e[0] for e in entity_types],
            "entity_type_count": len(entity_types),
        }

    except Exception as e:
        logger.error("Failed to get memory stats", error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve memory statistics",
        )


# ============================================================
# Local Run
# ============================================================

if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.environment == "development",
        log_level=settings.log_level.lower(),
    )

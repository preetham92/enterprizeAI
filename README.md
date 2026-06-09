# EnterprizeAI — AI Orchestration Platform

A multi-agent AI system built with FastAPI, designed for enterprise procurement and contract management workflows. The platform routes incoming queries through a central orchestrator to a suite of specialized AI agents, each handling a distinct domain such as contract review, vendor selection, fraud detection, and negotiation strategy.

---

## Features

- **Central Orchestrator** — Intelligently routes user queries to the most relevant agents and aggregates their outputs into a unified response.
- **14 Specialized Agents** — Domain-specific agents covering the full procurement and contract lifecycle.
- **PostgreSQL Memory** — Persistent memory layer backed by SQLAlchemy and PostgreSQL for storing agent context and entity history.
- **Live Web Search** — Search agent powered by Playwright and BeautifulSoup for real-time supplier and market intelligence.
- **REST API** — FastAPI-based interface with structured request/response models, health checks, and memory statistics endpoints.
- **Docker Support** — Full Docker Compose setup with PostgreSQL and the orchestration service.
- **Structured Logging** — JSON-formatted logs via `structlog` for observability.
- **Test Suite** — Comprehensive async test runner covering all 14 agents and the full orchestrator integration flow.

---

## Agents

| Agent | Task Type | Description |
|---|---|---|
| Search Agent | `SEARCH` | Live web search for supplier and market data |
| Document Automation Agent | `DOCUMENT_ANALYSIS` | Contract generation and document automation |
| RFQ/RFP Anomaly Agent | `FRAUD_DETECTION` | Detects pricing and bidding anomalies in RFQ/RFP responses |
| Vendor Selection Agent | `ANALYTICS_FORECAST` | Weighted scoring and vendor ranking |
| Enhanced Negotiation Agent | `NEGOTIATION_STRATEGY` | Counter-offer and negotiation strategy generation |
| Contract Review Agent | `DOCUMENT_ANALYSIS` | Flags deviations from standard contract templates |
| Change Order Agent | `ANALYTICS_FORECAST` | Analyzes cost and schedule impact of change orders |
| Predictive Analytics Agent | `ANALYTICS_FORECAST` | Forecasts costs and timelines from historical data |
| Records Keeping Agent | `ANALYTICS_FORECAST` | Creates project benchmarks and maintains records |
| Document/Contract Agent | `DOCUMENT_ANALYSIS` | Clause extraction and contract analysis |
| Risk & Compliance Agent | `RISK_COMPLIANCE` | Legal and regulatory risk assessment |
| Basic Negotiation Agent | `NEGOTIATION_STRATEGY` | Core negotiation strategy development |
| Analytics & Forecast Agent | `ANALYTICS_FORECAST` | Timeline and resource forecasting |
| Fraud & Anomaly Agent | `FRAUD_DETECTION` | Invoice and transaction fraud detection |

---

## Project Structure

```
enterprizeAI/
├── main.py                   # FastAPI app — routes, middleware, lifespan
├── docker-compose.yml        # PostgreSQL + orchestrator services
├── dockerfile
├── requirements.txt
├── pytest.ini
├── test_all_agents.py        # Full agent + orchestrator test suite
├── .env                      # Environment variables (not committed)
├── config/                   # App settings (pydantic-settings)
├── src/
│   ├── agents/               # All 14 specialized agents
│   ├── orchestrator/         # Central orchestrator logic
│   ├── memory/               # Database manager and memory models
│   ├── models/               # Pydantic core models (AgentInput, OrchestratorRequest, etc.)
│   ├── api/routes/           # Additional API routers (e.g. memory routes)
│   └── utils/                # Logging utilities
├── examples/                 # Usage examples
└── tests/                    # Unit tests
```

---

## Prerequisites

- Python 3.11+
- Docker & Docker Compose
- PostgreSQL 16 (or use the provided Docker service)
- An [Ollama](https://ollama.com) instance (default model: `qwen3:8b`)

---

## Getting Started

### 1. Clone the repository

```bash
git clone https://github.com/preetham92/enterprizeAI.git
cd enterprizeAI
```

### 2. Configure environment variables

Copy and edit the `.env` file:

```bash
cp .env .env.local
```

Key variables:

```env
DATABASE_URL=postgresql+psycopg2://orchestrator:changeme@localhost:5432/ai_orchestration
OLLAMA_BASE_URL=https://your-ollama-instance/ollama
OLLAMA_MODEL=qwen3:8b
ENVIRONMENT=development
LOG_LEVEL=INFO
RESEARCH_SERVICE_URL=http://research_service:8000
RESEARCH_SERVICE_TIMEOUT=600
```

### 3. Run with Docker Compose

```bash
docker-compose up --build
```

This starts:
- **PostgreSQL 16** on port `5432`
- **AI Orchestrator API** on port `8000`

### 4. Run locally (without Docker)

```bash
python -m venv venv
source venv/bin/activate       # Windows: venv\Scripts\activate
pip install -r requirements.txt
playwright install chromium     # Required for the Search Agent

python main.py
```

---

## API Reference

### POST `/orchestrate`

Main entry point. Routes the query through the orchestrator to relevant agents.

**Request body:**
```json
{
  "user_query": "Check this contract for liability risks and negotiate better terms.",
  "document_text": "The Provider's liability shall be limited to $100. Payment is Net 90.",
  "domain_context": { "priority": "high" }
}
```

**Response:**
```json
{
  "request_id": "...",
  "response": "...",
  "agent_outputs": [...],
  "confidence": 0.87,
  "execution_time_ms": 1240,
  "metadata": {}
}
```

### GET `/agents`

Lists all registered agents and their count.

### GET `/health`

Returns service health and database connectivity status.

### GET `/memory/stats`

Returns total memory entries and entity type breakdown from the PostgreSQL store.

---

## Running Tests

```bash
pytest pytest.ini

# Or run the full agent integration test directly:
python test_all_agents.py
```

The test suite runs all 14 agents with representative inputs and then exercises the full orchestrator flow, reporting pass/fail, confidence scores, and execution times. Results are saved as a timestamped JSON file.

---

## Tech Stack

| Layer | Technology |
|---|---|
| API Framework | FastAPI + Uvicorn |
| Data Validation | Pydantic v2 |
| Database ORM | SQLAlchemy 2.0 + Alembic |
| Database | PostgreSQL 16 |
| HTTP Clients | httpx, aiohttp, requests |
| Web Scraping | Playwright, BeautifulSoup4, lxml |
| Logging | structlog, python-json-logger |
| Testing | pytest, pytest-asyncio, pytest-cov |
| Containerization | Docker, Docker Compose |

---

## Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/my-agent`)
3. Commit your changes
4. Push and open a pull request

---

## License

This project does not currently specify a license. Please contact the repository owner for usage terms.

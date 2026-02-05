import asyncio
import httpx


# =========================
# Configuration
# =========================
API_BASE_URL = "http://localhost:8000"
TIMEOUT = 120.0


# =========================
# Helpers
# =========================

def print_section(title: str):
    print("\n" + "=" * 60)
    print(title)
    print("=" * 60)


def safe_get(d: dict, key: str, default="N/A"):
    return d.get(key, default) if isinstance(d, dict) else default


# =========================
# Examples
# =========================

async def check_health():
    async with httpx.AsyncClient(timeout=TIMEOUT) as client:
        response = await client.get(f"{API_BASE_URL}/health")
        health = response.json()

        print_section("Platform Health")
        print(f"Status   : {safe_get(health, 'status')}")
        print(f"Database : {safe_get(health, 'database')}")
        print(f"Time     : {safe_get(health, 'timestamp')}")


async def list_agents():
    async with httpx.AsyncClient(timeout=TIMEOUT) as client:
        response = await client.get(f"{API_BASE_URL}/agents")
        data = response.json()

        print_section("Available Agents")
        for agent in data.get("agents", []):
            print(f"\n• {agent.get('name', 'unknown')}")
            print(f"  Capabilities: {', '.join(agent.get('capabilities', []))}")


async def example_vendor_search():
    async with httpx.AsyncClient(timeout=TIMEOUT) as client:
        payload = {
            "user_query": "Find reliable solar panel installation vendors in Bengaluru",
            "domain_context": {
                "domain": "renewable_energy",
                "location": "Bengaluru",
                "service_type": "solar_installation"
            }
        }

        response = await client.post(f"{API_BASE_URL}/orchestrate", json=payload)
        result = response.json()

        print_section("Vendor Search Results")
        print(f"Request ID : {safe_get(result, 'request_id')}")
        print(f"Confidence : {safe_get(result, 'confidence')}")
        print(f"Time (ms)  : {safe_get(result, 'execution_time_ms')}")

        print("\nAnswer:")
        print(safe_get(result.get("answer", {}), "summary"))


async def example_contract_analysis():
    async with httpx.AsyncClient(timeout=TIMEOUT) as client:
        payload = {
            "user_query": "Analyze this contract for compliance and risk issues",
            "domain_context": {
                "domain": "legal",
                "analysis_type": "compliance_risk"
            },
            "constraints": {
                "document_text": """
                This Service Agreement is entered into on January 1, 2026
                between Client Corp and Service Provider LLC.

                Payment Terms: Net 90 days from invoice date.
                Liability: Provider's liability is limited to service fees paid.
                Termination: Either party may terminate with 30 days notice.
                Governing Law: State of Delaware.
                """
            }
        }

        response = await client.post(f"{API_BASE_URL}/orchestrate", json=payload)
        result = response.json()

        print_section("Contract Analysis")
        print(f"Confidence : {safe_get(result, 'confidence')}")
        print("\nAnalysis:")
        print(safe_get(result.get("answer", {}), "summary"))


async def example_fraud_detection():
    async with httpx.AsyncClient(timeout=TIMEOUT) as client:
        payload = {
            "user_query": "Check these invoices for irregularities and fraud indicators",
            "domain_context": {
                "domain": "finance",
                "detection_type": "invoice_fraud"
            },
            "constraints": {
                "transaction_data": """
                Invoice #1001: $45,000 - Office Supplies - Vendor: ABC Corp
                Invoice #1002: $12,300 - IT Services - Vendor: Tech Solutions
                Invoice #1003: $450,000 - Office Supplies - Vendor: ABC Corp
                Invoice #1004: $8,500 - Consulting - Vendor: Advisors Inc
                """
            }
        }

        response = await client.post(f"{API_BASE_URL}/orchestrate", json=payload)
        result = response.json()

        print_section("Fraud Detection")
        print(f"Confidence : {safe_get(result, 'confidence')}")
        print("\nFindings:")
        print(safe_get(result.get("answer", {}), "summary"))


async def example_forecasting():
    async with httpx.AsyncClient(timeout=TIMEOUT) as client:
        payload = {
            "user_query": "Forecast the cost and timeline for this construction project",
            "domain_context": {
                "domain": "construction",
                "forecast_type": "cost_timeline"
            },
            "constraints": {
                "historical_data": """
                Similar Projects:
                - Hospital Wing (2023): $85M, 22 months
                - Medical Center (2024): $120M, 26 months
                - Clinic Expansion (2025): $45M, 14 months

                Current Project: 150-bed hospital, 200,000 sq ft
                Location: Urban area with high labor costs
                """
            }
        }

        response = await client.post(f"{API_BASE_URL}/orchestrate", json=payload)
        result = response.json()

        print_section("Forecasting")
        print(f"Confidence : {safe_get(result, 'confidence')}")
        print("\nForecast:")
        print(safe_get(result.get("answer", {}), "summary"))


# =========================
# Runner
# =========================

async def main():
    print("\nAI Orchestration Platform — Example Usage")
    print("=" * 60)

    await check_health()
    await list_agents()
    await example_vendor_search()
    await example_contract_analysis()
    await example_fraud_detection()
    await example_forecasting()

    print("\n" + "=" * 60)
    print("All examples completed successfully ✔")


if __name__ == "__main__":
    asyncio.run(main())

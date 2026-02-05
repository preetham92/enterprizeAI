"""
LLM Client for Qwen3:8b via Ollama API.
Handles all communication with the language model.
"""
from typing import AsyncGenerator, Dict, Any, Optional
import asyncio
import httpx
import json
from config.settings import settings
from src.utils.logging import get_logger
from src.models.core import LLMRequest, LLMResponse

logger = get_logger(__name__)


class LLMClient:
    """
    Client for interacting with Qwen3:8b via Ollama API.
    Treats LLM as pure text-in/text-out reasoning engine.
    """
    
    def __init__(self):
        self.base_url = settings.ollama_base_url
        self.model = settings.ollama_model
        self.timeout = settings.ollama_timeout
        self.max_retries = settings.ollama_max_retries
        
    async def generate(
        self,
        prompt: str,
        stream: bool = True,
        temperature: float = 0.7,
        max_tokens: Optional[int] = None
    ) -> str:
        """
        Generate text from the LLM.
        
        Args:
            prompt: The prompt to send to the LLM
            stream: Whether to use streaming (True by default)
            temperature: Sampling temperature
            max_tokens: Maximum tokens to generate
            
        Returns:
            Generated text
        """
        endpoint = f"{self.base_url}/api/generate"
        
        request_data = {
            "model": self.model,
            "prompt": prompt,
            "stream": stream,
            "options": {
                "temperature": temperature,
            }
        }
        
        if max_tokens:
            request_data["options"]["num_predict"] = max_tokens
        
        logger.info(
            "Sending request to LLM",
            model=self.model,
            prompt_length=len(prompt),
            stream=stream
        )
        
        for attempt in range(self.max_retries):
            try:
                if stream:
                    return await self._generate_streaming(endpoint, request_data)
                else:
                    return await self._generate_non_streaming(endpoint, request_data)
                    
            except Exception as e:
                logger.warning(
                    "LLM request failed",
                    attempt=attempt + 1,
                    max_retries=self.max_retries,
                    error=str(e)
                )
                
                if attempt == self.max_retries - 1:
                    logger.error("LLM request failed after all retries", error=str(e))
                    raise
                
                await asyncio.sleep(2 ** attempt)  # Exponential backoff
        
        raise RuntimeError("Failed to get LLM response")
    
    async def _generate_streaming(self, endpoint: str, request_data: Dict) -> str:
        """Generate text using streaming API."""
        full_response = ""
        
        async with httpx.AsyncClient(timeout=self.timeout) as client:
            async with client.stream("POST", endpoint, json=request_data) as response:
                response.raise_for_status()
                
                async for line in response.aiter_lines():
                    if not line.strip():
                        continue
                    
                    try:
                        data = json.loads(line)
                        
                        if "response" in data:
                            full_response += data["response"]
                        
                        if data.get("done", False):
                            logger.info(
                                "LLM generation complete",
                                response_length=len(full_response),
                                eval_count=data.get("eval_count")
                            )
                            break
                            
                    except json.JSONDecodeError:
                        logger.warning("Failed to parse LLM response line", line=line)
                        continue
        
        return full_response.strip()
    
    async def _generate_non_streaming(self, endpoint: str, request_data: Dict) -> str:
        """Generate text using non-streaming API."""
        async with httpx.AsyncClient(timeout=self.timeout) as client:
            response = await client.post(endpoint, json=request_data)
            response.raise_for_status()
            
            data = response.json()
            
            logger.info(
                "LLM generation complete",
                response_length=len(data.get("response", "")),
                eval_count=data.get("eval_count")
            )
            
            return data.get("response", "").strip()
    
    async def classify_intent(self, user_query: str) -> Dict[str, Any]:
        """
        Classify user intent and extract key information.
        
        Returns:
            Dictionary with intent, entities, and task breakdown
        """
        prompt = f"""Analyze this user query and extract:
1. Primary intent/goal
2. Key entities mentioned (vendors, contracts, regulations, etc.)
3. Required tasks to fulfill the request
4. Domain context

User Query: {user_query}

Respond in JSON format:
{{
    "intent": "brief description of intent",
    "entities": ["entity1", "entity2"],
    "required_tasks": ["task1", "task2"],
    "domain": "domain name or 'generic'"
}}"""

        response = await self.generate(prompt, temperature=0.3)
        
        try:
            # Extract JSON from response
            start_idx = response.find('{')
            end_idx = response.rfind('}') + 1
            
            if start_idx >= 0 and end_idx > start_idx:
                json_str = response[start_idx:end_idx]
                return json.loads(json_str)
            else:
                logger.warning("No JSON found in classification response")
                return {
                    "intent": user_query,
                    "entities": [],
                    "required_tasks": ["search"],
                    "domain": "generic"
                }
        except json.JSONDecodeError as e:
            logger.error("Failed to parse classification JSON", error=str(e))
            return {
                "intent": user_query,
                "entities": [],
                "required_tasks": ["search"],
                "domain": "generic"
            }
    
    async def synthesize_response(
        self,
        query: str,
        agent_outputs: list,
        memory_context: Optional[list] = None
    ) -> str:
        """
        Synthesize final response from agent outputs.
        
        Args:
            query: Original user query
            agent_outputs: List of agent outputs
            memory_context: Optional historical context
            
        Returns:
            Synthesized natural language response
        """
        # Build context from agent outputs
        agent_results = []
        for output in agent_outputs:
            agent_results.append(
                f"Agent: {output.agent_name}\n"
                f"Confidence: {output.confidence}\n"
                f"Result: {output.result}\n"
                f"Sources: {', '.join(output.sources)}"
            )
        
        memory_section = ""
        if memory_context:
            memory_section = "\nHistorical Context:\n" + "\n".join(
                [f"- {item}" for item in memory_context[:3]]
            )
        
        prompt = f"""Synthesize a clear, accurate response to the user's query based on agent findings.

User Query: {query}

Agent Findings:
{chr(10).join(agent_results)}
{memory_section}

Provide a comprehensive answer that:
1. Directly addresses the user's question
2. Integrates information from multiple agents
3. Highlights important sources
4. Notes any uncertainties or conflicts
5. Is clear and actionable

Response:"""

        return await self.generate(prompt, temperature=0.5)


# Global LLM client instance
llm_client = LLMClient()
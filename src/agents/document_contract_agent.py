"""
Document/Contract Agent - Handles document analysis, clause extraction,
deviation detection, and contract-related tasks.
"""
from typing import Dict, Any
from datetime import datetime
from src.utils.logging import get_logger
from src.models.core import AgentInput, AgentOutput
from src.core.llm_client import llm_client

logger = get_logger(__name__)


class DocumentContractAgent:
    """
    Document/Contract Agent.
    Performs clause extraction, deviation detection, RAG tagging.
    """
    
    name = "document_contract_agent"
    capabilities = [
        "clause_extraction",
        "deviation_detection",
        "rag_tagging",
        "change_order_analysis",
        "contract_review"
    ]
    
    async def execute(self, agent_input: AgentInput) -> AgentOutput:
        """Execute document/contract analysis."""
        start_time = datetime.utcnow()
        
        logger.info(
            "Document/Contract agent executing",
            task_id=str(agent_input.task_id)
        )
        
        try:
            # Extract document content from context
            document_text = agent_input.context.get("document_text", "")
            analysis_type = agent_input.context.get("analysis_type", "general")
            
            # Build analysis prompt
            prompt = self._build_analysis_prompt(
                document_text,
                analysis_type,
                agent_input.instructions,
                agent_input.memory_context
            )
            
            # Get analysis from LLM
            analysis = await llm_client.generate(prompt, temperature=0.3)
            
            # Structure the results
            result = self._structure_analysis(analysis, analysis_type)
            
            # Calculate confidence
            confidence = self._calculate_confidence(result)
            
            execution_time = (datetime.utcnow() - start_time).total_seconds() * 1000
            
            logger.info(
                "Document/Contract agent completed",
                task_id=str(agent_input.task_id),
                confidence=confidence
            )
            
            return AgentOutput(
                task_id=agent_input.task_id,
                agent_name=self.name,
                result=result,
                confidence=confidence,
                execution_time_ms=execution_time,
                metadata={"analysis_type": analysis_type}
            )
            
        except Exception as e:
            logger.error(
                "Document/Contract agent failed",
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
    
    def _build_analysis_prompt(
        self,
        document_text: str,
        analysis_type: str,
        instructions: str,
        memory_context: Any
    ) -> str:
        """Build prompt for document analysis."""
        
        memory_section = ""
        if memory_context:
            memory_section = "\n\nHistorical Context:\n"
            for item in memory_context[:3]:
                memory_section += f"- {item}\n"
        
        if analysis_type == "clause_extraction":
            prompt = f"""Extract and categorize all key clauses from this contract.

Document:
{document_text[:5000]}

{instructions}
{memory_section}

Provide analysis in this format:
- Key Clauses: List main contract clauses
- Payment Terms: Extract payment-related clauses
- Liability Terms: Extract liability and indemnity clauses
- Termination Clauses: Extract termination conditions
- Non-Standard Clauses: Identify unusual or custom clauses

Analysis:"""

        elif analysis_type == "deviation_detection":
            prompt = f"""Analyze this contract for deviations from standard terms (GCC/SCC patterns).

Document:
{document_text[:5000]}

{instructions}
{memory_section}

Identify:
1. Deviations from standard terms
2. Risk level (Red/Amber/Green) for each deviation
3. Recommended actions

Analysis:"""

        elif analysis_type == "change_order":
            prompt = f"""Analyze this change order or variation request.

Document:
{document_text[:5000]}

{instructions}
{memory_section}

Provide:
1. Nature of changes
2. Cost impact
3. Timeline impact
4. Risk assessment
5. Approval recommendation

Analysis:"""

        else:
            prompt = f"""Analyze this document and provide comprehensive insights.

Document:
{document_text[:5000]}

{instructions}
{memory_section}

Analysis:"""
        
        return prompt
    
    def _structure_analysis(self, analysis: str, analysis_type: str) -> Dict[str, Any]:
        """Structure the LLM analysis into a standard format."""
        return {
            "analysis_type": analysis_type,
            "full_analysis": analysis,
            "summary": analysis[:500] + "..." if len(analysis) > 500 else analysis,
            "timestamp": datetime.utcnow().isoformat()
        }
    
    def _calculate_confidence(self, result: Dict[str, Any]) -> float:
        """Calculate confidence in the analysis."""
        # Base confidence for document analysis
        confidence = 0.75
        
        # Increase if analysis is comprehensive
        if len(result.get("full_analysis", "")) > 200:
            confidence += 0.1
        
        return min(confidence, 0.95)


# Global document/contract agent instance
document_contract_agent = DocumentContractAgent()
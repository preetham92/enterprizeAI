"""
Document Automation Agent - Automates contract creation and approval workflows.
Handles template selection, clause insertion, approval routing, and document generation.
"""
from typing import Dict, Any, List, Optional
from datetime import datetime
import json
from src.utils.logging import get_logger
from src.models.core import AgentInput, AgentOutput, TaskType
from src.core.llm_client import llm_client

logger = get_logger(__name__)


class DocumentAutomationAgent:
    """
    Document Automation Agent.
    Automates contract creation, clause generation, and approval workflows.
    """
    
    name = "document_automation_agent"
    capabilities = [
        "contract_generation",
        "template_selection",
        "clause_automation",
        "approval_workflow_routing",
        "document_assembly",
        "version_control",
        "stakeholder_identification"
    ]
    
    async def execute(self, agent_input: AgentInput) -> AgentOutput:
        """Execute document automation task."""
        start_time = datetime.utcnow()
        
        logger.info(
            "Document Automation agent executing",
            task_id=str(agent_input.task_id),
            automation_type=agent_input.context.get("automation_type", "general")
        )
        
        try:
            automation_type = agent_input.context.get("automation_type", "contract_generation")
            
            if automation_type == "contract_generation":
                result = await self._generate_contract(agent_input)
            elif automation_type == "approval_workflow":
                result = await self._create_approval_workflow(agent_input)
            elif automation_type == "clause_insertion":
                result = await self._insert_clauses(agent_input)
            elif automation_type == "template_selection":
                result = await self._select_template(agent_input)
            else:
                result = await self._general_automation(agent_input)
            
            confidence = self._calculate_confidence(result)
            sources = self._extract_sources(result)
            
            execution_time = (datetime.utcnow() - start_time).total_seconds() * 1000
            
            logger.info(
                "Document Automation agent completed",
                task_id=str(agent_input.task_id),
                automation_type=automation_type,
                confidence=confidence
            )
            
            return AgentOutput(
                task_id=agent_input.task_id,
                agent_name=self.name,
                result=result,
                confidence=confidence,
                sources=sources,
                execution_time_ms=execution_time,
                metadata={
                    "automation_type": automation_type,
                    "document_sections": len(result.get("sections", []))
                }
            )
            
        except Exception as e:
            logger.error(
                "Document Automation agent failed",
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
    
    async def _generate_contract(self, agent_input: AgentInput) -> Dict[str, Any]:
        """Generate complete contract from requirements."""
        requirements = agent_input.context.get("requirements", {})
        contract_type = agent_input.context.get("contract_type", "service_agreement")
        parties = agent_input.context.get("parties", {})
        
        memory_context_str = ""
        if agent_input.memory_context:
            memory_context_str = "\n\nHistorical Context:\n" + "\n".join(
                [f"- {item.get('content', {}).get('result', '')}" for item in agent_input.memory_context[:3]]
            )
        
        prompt = f"""Generate a comprehensive {contract_type} contract based on requirements.

Parties:
Client: {parties.get('client', 'Not specified')}
Provider: {parties.get('provider', 'Not specified')}

Requirements:
{json.dumps(requirements, indent=2)}

Instructions: {agent_input.instructions}
{memory_context_str}

Generate a complete contract with the following sections:
1. TITLE AND PARTIES
2. RECITALS (Background and context)
3. DEFINITIONS
4. SCOPE OF WORK/SERVICES
5. PAYMENT TERMS
6. TIMELINE AND MILESTONES
7. RESPONSIBILITIES AND OBLIGATIONS
8. INTELLECTUAL PROPERTY RIGHTS
9. CONFIDENTIALITY
10. WARRANTIES AND REPRESENTATIONS
11. LIMITATION OF LIABILITY
12. INDEMNIFICATION
13. TERMINATION
14. DISPUTE RESOLUTION
15. GENERAL PROVISIONS
16. SIGNATURES

For each section, provide:
- Section heading
- Complete clause text
- Notes on customization needed
- Risk level (Low/Medium/High)

Provide output in JSON format:
{{
    "contract_title": "Title",
    "contract_type": "{contract_type}",
    "parties": {{}},
    "sections": [
        {{
            "section_number": 1,
            "section_title": "Title",
            "clauses": [
                {{
                    "clause_id": "1.1",
                    "clause_text": "Text",
                    "customization_notes": "Notes",
                    "risk_level": "Low"
                }}
            ]
        }}
    ],
    "approval_requirements": [],
    "next_steps": []
}}

Contract:"""

        response = await llm_client.generate(prompt, temperature=0.4)
        
        try:
            # Extract JSON from response
            start_idx = response.find('{')
            end_idx = response.rfind('}') + 1
            
            if start_idx >= 0 and end_idx > start_idx:
                json_str = response[start_idx:end_idx]
                contract_data = json.loads(json_str)
            else:
                # Fallback structured response
                contract_data = self._create_fallback_contract(response, contract_type, parties)
            
            # Add metadata
            contract_data["generated_at"] = datetime.utcnow().isoformat()
            contract_data["status"] = "draft"
            contract_data["workflow_stage"] = "initial_generation"
            
            return contract_data
            
        except json.JSONDecodeError:
            logger.warning("Failed to parse contract JSON, using structured fallback")
            return self._create_fallback_contract(response, contract_type, parties)
    
    async def _create_approval_workflow(self, agent_input: AgentInput) -> Dict[str, Any]:
        """Create approval workflow based on contract type and value."""
        contract_data = agent_input.context.get("contract_data", {})
        contract_value = agent_input.context.get("contract_value", 0)
        contract_type = agent_input.context.get("contract_type", "general")
        organization_rules = agent_input.context.get("organization_rules", {})
        
        prompt = f"""Design an approval workflow for this contract.

Contract Type: {contract_type}
Contract Value: ${contract_value:,.2f}
Organization Rules: {json.dumps(organization_rules, indent=2)}

Contract Summary:
{json.dumps(contract_data, indent=2)[:1000]}

Instructions: {agent_input.instructions}

Create a comprehensive approval workflow with:
1. Approval stages (sequential or parallel)
2. Required approvers at each stage
3. Approval criteria and checkpoints
4. Escalation paths
5. Timeline for each stage
6. Documents required at each stage
7. Notifications and reminders

Consider:
- Contract value thresholds
- Risk level
- Department involvement
- Legal review requirements
- Executive approval needs
- Compliance checkpoints

Provide in JSON format:
{{
    "workflow_id": "unique_id",
    "workflow_type": "sequential/parallel/hybrid",
    "total_stages": 0,
    "estimated_duration_days": 0,
    "stages": [
        {{
            "stage_number": 1,
            "stage_name": "Name",
            "stage_type": "sequential/parallel",
            "approvers": [
                {{
                    "role": "Role",
                    "name": "Name",
                    "authority_level": "Level",
                    "approval_criteria": ["criterion1"]
                }}
            ],
            "required_documents": [],
            "sla_days": 0,
            "escalation_path": "",
            "notifications": []
        }}
    ],
    "conditional_routing": [],
    "final_approver": "",
    "post_approval_actions": []
}}

Workflow:"""

        response = await llm_client.generate(prompt, temperature=0.3)
        
        try:
            start_idx = response.find('{')
            end_idx = response.rfind('}') + 1
            
            if start_idx >= 0 and end_idx > start_idx:
                json_str = response[start_idx:end_idx]
                workflow_data = json.loads(json_str)
            else:
                workflow_data = self._create_fallback_workflow(contract_type, contract_value)
            
            workflow_data["created_at"] = datetime.utcnow().isoformat()
            workflow_data["status"] = "pending_initiation"
            
            return workflow_data
            
        except json.JSONDecodeError:
            return self._create_fallback_workflow(contract_type, contract_value)
    
    async def _insert_clauses(self, agent_input: AgentInput) -> Dict[str, Any]:
        """Insert or update specific clauses in a contract."""
        contract_text = agent_input.context.get("contract_text", "")
        clause_requirements = agent_input.context.get("clause_requirements", [])
        
        prompt = f"""Update contract with required clauses.

Current Contract:
{contract_text[:2000]}

Required Clause Updates:
{json.dumps(clause_requirements, indent=2)}

Instructions: {agent_input.instructions}

For each required clause:
1. Identify insertion point
2. Draft complete clause text
3. Ensure consistency with existing clauses
4. Flag any conflicts
5. Provide reasoning

Output JSON:
{{
    "clause_insertions": [
        {{
            "clause_type": "Type",
            "insertion_point": "Section X",
            "clause_text": "Full text",
            "rationale": "Why needed",
            "conflicts": [],
            "risk_mitigation": "How it reduces risk"
        }}
    ],
    "updated_contract_outline": [],
    "review_notes": []
}}

Analysis:"""

        response = await llm_client.generate(prompt, temperature=0.3)
        
        try:
            start_idx = response.find('{')
            end_idx = response.rfind('}') + 1
            
            if start_idx >= 0 and end_idx > start_idx:
                json_str = response[start_idx:end_idx]
                return json.loads(json_str)
        except json.JSONDecodeError:
            pass
        
        return {
            "clause_insertions": [],
            "analysis": response,
            "status": "manual_review_required"
        }
    
    async def _select_template(self, agent_input: AgentInput) -> Dict[str, Any]:
        """Select appropriate contract template based on requirements."""
        requirements = agent_input.context.get("requirements", {})
        available_templates = agent_input.context.get("available_templates", [])
        
        prompt = f"""Select the most appropriate contract template.

Requirements:
{json.dumps(requirements, indent=2)}

Available Templates:
{json.dumps(available_templates, indent=2)}

Instructions: {agent_input.instructions}

Analyze and recommend:
1. Best matching template
2. Required customizations
3. Alternative templates
4. Risk assessment

Output JSON:
{{
    "recommended_template": {{
        "template_id": "ID",
        "template_name": "Name",
        "match_score": 0.95,
        "match_reasoning": "Why this template"
    }},
    "required_customizations": [],
    "alternative_templates": [],
    "risk_assessment": {{
        "overall_risk": "Low/Medium/High",
        "risk_factors": []
    }}
}}

Recommendation:"""

        response = await llm_client.generate(prompt, temperature=0.3)
        
        try:
            start_idx = response.find('{')
            end_idx = response.rfind('}') + 1
            
            if start_idx >= 0 and end_idx > start_idx:
                json_str = response[start_idx:end_idx]
                return json.loads(json_str)
        except json.JSONDecodeError:
            pass
        
        return {
            "recommended_template": {},
            "analysis": response
        }
    
    async def _general_automation(self, agent_input: AgentInput) -> Dict[str, Any]:
        """Handle general document automation tasks."""
        task_description = agent_input.instructions
        context = agent_input.context
        
        prompt = f"""Automate document creation task.

Task: {task_description}
Context: {json.dumps(context, indent=2)[:1000]}

Provide comprehensive automation plan and execution.

Plan:"""

        response = await llm_client.generate(prompt, temperature=0.4)
        
        return {
            "automation_plan": response,
            "status": "completed",
            "timestamp": datetime.utcnow().isoformat()
        }
    
    def _create_fallback_contract(
        self,
        llm_response: str,
        contract_type: str,
        parties: Dict
    ) -> Dict[str, Any]:
        """Create structured fallback contract when JSON parsing fails."""
        return {
            "contract_title": f"{contract_type.replace('_', ' ').title()}",
            "contract_type": contract_type,
            "parties": parties,
            "sections": [
                {
                    "section_number": 1,
                    "section_title": "Generated Contract Content",
                    "clauses": [
                        {
                            "clause_id": "1.1",
                            "clause_text": llm_response,
                            "customization_notes": "Review and structure as needed",
                            "risk_level": "Medium"
                        }
                    ]
                }
            ],
            "approval_requirements": ["Legal Review", "Management Approval"],
            "next_steps": ["Review generated content", "Structure sections", "Customize clauses"],
            "generated_at": datetime.utcnow().isoformat(),
            "status": "draft_requires_review"
        }
    
    def _create_fallback_workflow(
        self,
        contract_type: str,
        contract_value: float
    ) -> Dict[str, Any]:
        """Create fallback approval workflow."""
        stages = []
        
        # Determine stages based on contract value
        if contract_value < 50000:
            stages = [
                {
                    "stage_number": 1,
                    "stage_name": "Department Head Approval",
                    "stage_type": "sequential",
                    "approvers": [{"role": "Department Head", "name": "TBD"}],
                    "sla_days": 2
                },
                {
                    "stage_number": 2,
                    "stage_name": "Legal Review",
                    "stage_type": "sequential",
                    "approvers": [{"role": "Legal Counsel", "name": "TBD"}],
                    "sla_days": 3
                }
            ]
        elif contract_value < 500000:
            stages = [
                {
                    "stage_number": 1,
                    "stage_name": "Department Approval",
                    "stage_type": "parallel",
                    "approvers": [
                        {"role": "Department Head", "name": "TBD"},
                        {"role": "Finance Manager", "name": "TBD"}
                    ],
                    "sla_days": 3
                },
                {
                    "stage_number": 2,
                    "stage_name": "Legal Review",
                    "stage_type": "sequential",
                    "approvers": [{"role": "Legal Counsel", "name": "TBD"}],
                    "sla_days": 5
                },
                {
                    "stage_number": 3,
                    "stage_name": "Executive Approval",
                    "stage_type": "sequential",
                    "approvers": [{"role": "VP/Director", "name": "TBD"}],
                    "sla_days": 2
                }
            ]
        else:
            stages = [
                {
                    "stage_number": 1,
                    "stage_name": "Multi-Department Review",
                    "stage_type": "parallel",
                    "approvers": [
                        {"role": "Department Head", "name": "TBD"},
                        {"role": "Finance Director", "name": "TBD"},
                        {"role": "Procurement Head", "name": "TBD"}
                    ],
                    "sla_days": 5
                },
                {
                    "stage_number": 2,
                    "stage_name": "Legal & Compliance Review",
                    "stage_type": "parallel",
                    "approvers": [
                        {"role": "Legal Counsel", "name": "TBD"},
                        {"role": "Compliance Officer", "name": "TBD"}
                    ],
                    "sla_days": 7
                },
                {
                    "stage_number": 3,
                    "stage_name": "Executive Approval",
                    "stage_type": "sequential",
                    "approvers": [{"role": "C-Level Executive", "name": "TBD"}],
                    "sla_days": 3
                }
            ]
        
        return {
            "workflow_id": f"WF-{datetime.utcnow().strftime('%Y%m%d%H%M%S')}",
            "workflow_type": "hybrid",
            "total_stages": len(stages),
            "estimated_duration_days": sum(s["sla_days"] for s in stages),
            "stages": stages,
            "created_at": datetime.utcnow().isoformat(),
            "status": "pending_initiation"
        }
    
    def _calculate_confidence(self, result: Dict[str, Any]) -> float:
        """Calculate confidence score for automation result."""
        confidence = 0.7  # Base confidence
        
        # Increase confidence if structured output
        if "sections" in result and len(result.get("sections", [])) > 0:
            confidence += 0.15
        
        if "stages" in result and len(result.get("stages", [])) > 0:
            confidence += 0.15
        
        # Check for completeness
        if result.get("status") == "completed":
            confidence += 0.05
        
        return min(confidence, 0.95)
    
    def _extract_sources(self, result: Dict[str, Any]) -> List[str]:
        """Extract reference sources from result."""
        sources = []
        
        # Add template references if any
        if "recommended_template" in result:
            template = result["recommended_template"]
            if template.get("template_id"):
                sources.append(f"Template: {template.get('template_name', template['template_id'])}")
        
        return sources


# Global document automation agent instance
document_automation_agent = DocumentAutomationAgent()
"""
Negotiation Strategy Agent - Advanced negotiation support with strategy notes,
counter-offers, leverage analysis, and tactical recommendations.
"""
from typing import Dict, Any, List, Optional
from datetime import datetime
import json
from src.utils.logging import get_logger
from src.models.core import AgentInput, AgentOutput
from src.core.llm_client import llm_client

logger = get_logger(__name__)


class NegotiationStrategyAgentEnhanced:
    """
    Enhanced Negotiation Strategy Agent.
    Provides comprehensive negotiation support with detailed strategy notes and counter-offers.
    """
    
    name = "negotiation_strategy_agent_enhanced"
    capabilities = [
        "strategy_development",
        "counter_offer_generation",
        "leverage_analysis",
        "batna_identification",
        "negotiation_planning",
        "tactical_recommendations",
        "concession_strategy",
        "relationship_management"
    ]
    
    async def execute(self, agent_input: AgentInput) -> AgentOutput:
        """Execute negotiation strategy analysis."""
        start_time = datetime.utcnow()
        
        logger.info(
            "Negotiation Strategy agent executing",
            task_id=str(agent_input.task_id)
        )
        
        try:
            strategy_type = agent_input.context.get("strategy_type", "comprehensive")
            
            if strategy_type == "counter_offer":
                result = await self._generate_counter_offer(agent_input)
            elif strategy_type == "leverage":
                result = await self._analyze_leverage(agent_input)
            elif strategy_type == "planning":
                result = await self._create_negotiation_plan(agent_input)
            elif strategy_type == "concession":
                result = await self._develop_concession_strategy(agent_input)
            else:
                result = await self._comprehensive_negotiation_strategy(agent_input)
            
            confidence = self._calculate_confidence(result)
            
            execution_time = (datetime.utcnow() - start_time).total_seconds() * 1000
            
            logger.info(
                "Negotiation Strategy agent completed",
                task_id=str(agent_input.task_id),
                confidence=confidence
            )
            
            return AgentOutput(
                task_id=agent_input.task_id,
                agent_name=self.name,
                result=result,
                confidence=confidence,
                execution_time_ms=execution_time,
                metadata={
                    "strategy_type": strategy_type
                }
            )
            
        except Exception as e:
            logger.error(
                "Negotiation Strategy agent failed",
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
    
    async def _generate_counter_offer(self, agent_input: AgentInput) -> Dict[str, Any]:
        """Generate detailed counter-offers with strategic rationale."""
        original_offer = agent_input.context.get("original_offer", {})
        our_position = agent_input.context.get("our_position", {})
        constraints = agent_input.context.get("constraints", {})
        
        memory_context_str = ""
        if agent_input.memory_context:
            memory_context_str = "\n\nHistorical Negotiation Context:\n" + "\n".join(
                [f"- {item}" for item in agent_input.memory_context[:3]]
            )
        
        prompt = f"""Generate strategic counter-offers for negotiation.

Original Offer:
{json.dumps(original_offer, indent=2)}

Our Position and Objectives:
{json.dumps(our_position, indent=2)}

Constraints:
{json.dumps(constraints, indent=2)}
{memory_context_str}

Instructions: {agent_input.instructions}

Develop counter-offer strategy:

1. COUNTER-OFFER OPTIONS
   - Aggressive counter-offer (push boundaries)
   - Balanced counter-offer (meet halfway)
   - Conservative counter-offer (minimal change)

2. FOR EACH COUNTER-OFFER:
   - Specific terms and conditions
   - Pricing adjustments
   - Timeline modifications
   - Scope changes
   - Payment terms
   - Other commercial terms

3. STRATEGIC RATIONALE
   - Why this counter-offer
   - Expected response
   - Fallback positions
   - Walk-away point

4. SUPPORTING ARGUMENTS
   - Market benchmarks
   - Cost justifications
   - Value propositions
   - Risk considerations

5. NEGOTIATION TACTICS
   - Opening position
   - Concession sequence
   - Bundling opportunities
   - Timing considerations

Output JSON:
{{
    "counter_offers": [
        {{
            "counter_offer_id": "CO-001",
            "approach": "Aggressive/Balanced/Conservative",
            "recommended": true,
            "terms": {{
                "pricing": {{
                    "original": 1000000,
                    "counter_offer": 850000,
                    "justification": "Market rate is...",
                    "negotiation_room": 50000
                }},
                "timeline": {{
                    "original": "12 months",
                    "counter_offer": "14 months",
                    "rationale": "Why needed"
                }},
                "payment_terms": {{
                    "original": "Net 30",
                    "counter_offer": "Net 60",
                    "reasoning": "Cash flow considerations"
                }},
                "scope": {{
                    "additions": [],
                    "removals": [],
                    "modifications": []
                }},
                "other_terms": {{}}
            }},
            "strategic_rationale": {{
                "opening_position": "Why we start here",
                "expected_response": "What we anticipate",
                "success_probability": 0.7,
                "risk_assessment": "Medium"
            }},
            "supporting_arguments": [
                {{
                    "argument": "Argument text",
                    "evidence": "Supporting data",
                    "strength": "Strong/Moderate/Weak"
                }}
            ],
            "fallback_positions": [
                {{
                    "position": "If they reject, we can...",
                    "terms": {{}},
                    "acceptability": "Acceptable/Last resort"
                }}
            ],
            "walk_away_conditions": []
        }}
    ],
    "negotiation_tactics": {{
        "opening_statement": "Text",
        "key_messages": [],
        "concession_sequence": [],
        "timing_recommendations": "",
        "relationship_approach": "Collaborative/Competitive"
    }},
    "contingency_plans": [],
    "success_metrics": []
}}

Counter-Offer Strategy:"""

        response = await llm_client.generate(prompt, temperature=0.4)
        
        try:
            start_idx = response.find('{')
            end_idx = response.rfind('}') + 1
            
            if start_idx >= 0 and end_idx > start_idx:
                json_str = response[start_idx:end_idx]
                return json.loads(json_str)
        except json.JSONDecodeError:
            pass
        
        return {
            "counter_offers": [],
            "strategy_text": response,
            "timestamp": datetime.utcnow().isoformat()
        }
    
    async def _analyze_leverage(self, agent_input: AgentInput) -> Dict[str, Any]:
        """Analyze negotiation leverage and power dynamics."""
        situation = agent_input.context.get("situation", "")
        parties = agent_input.context.get("parties", {})
        market_conditions = agent_input.context.get("market_conditions", {})
        
        prompt = f"""Analyze negotiation leverage and power dynamics.

Situation:
{situation}

Parties Involved:
{json.dumps(parties, indent=2)}

Market Conditions:
{json.dumps(market_conditions, indent=2)}

Instructions: {agent_input.instructions}

Analyze leverage across:

1. OUR LEVERAGE POINTS
   - Unique capabilities
   - Competitive advantages
   - Alternatives available (BATNA)
   - Timeline flexibility
   - Budget authority
   - Market position

2. THEIR LEVERAGE POINTS
   - Their unique value
   - Our dependencies
   - Their alternatives
   - Their constraints
   - Market power
   - Relationship importance

3. MARKET DYNAMICS
   - Supply and demand
   - Competitive landscape
   - Industry trends
   - Regulatory environment
   - Economic conditions

4. RELATIONSHIP FACTORS
   - History and trust
   - Future potential
   - Reputation concerns
   - Strategic alignment

5. SITUATIONAL FACTORS
   - Urgency levels
   - Budget cycles
   - Decision-making authority
   - Organizational politics

Output JSON:
{{
    "leverage_analysis": {{
        "our_leverage_score": 65,
        "their_leverage_score": 55,
        "power_balance": "Favorable/Balanced/Unfavorable",
        "leverage_gap": 10
    }},
    "our_strengths": [
        {{
            "strength": "Description",
            "impact": "High/Medium/Low",
            "how_to_use": "Tactical application"
        }}
    ],
    "our_weaknesses": [
        {{
            "weakness": "Description",
            "impact": "High/Medium/Low",
            "mitigation": "How to address"
        }}
    ],
    "their_strengths": [],
    "their_weaknesses": [],
    "batna_analysis": {{
        "our_batna": "Best alternative if no deal",
        "their_batna": "Their best alternative",
        "batna_strength": "Strong/Moderate/Weak"
    }},
    "leverage_tactics": [
        {{
            "tactic": "Tactic name",
            "description": "How to apply",
            "timing": "When to use",
            "risk": "Low/Medium/High"
        }}
    ],
    "recommendations": []
}}

Leverage Analysis:"""

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
            "leverage_analysis": {},
            "analysis_text": response
        }
    
    async def _create_negotiation_plan(self, agent_input: AgentInput) -> Dict[str, Any]:
        """Create comprehensive negotiation plan."""
        negotiation_context = agent_input.context.get("context", {})
        objectives = agent_input.context.get("objectives", [])
        
        prompt = f"""Create comprehensive negotiation plan.

Context:
{json.dumps(negotiation_context, indent=2)}

Objectives:
{json.dumps(objectives, indent=2)}

Instructions: {agent_input.instructions}

Develop complete negotiation plan:

1. PREPARATION PHASE
   - Information gathering
   - Team selection
   - Role assignments
   - Internal alignment
   - Venue and logistics

2. OPENING PHASE
   - Initial positioning
   - Relationship building
   - Agenda setting
   - Information exchange
   - Opening offer

3. BARGAINING PHASE
   - Issues to discuss
   - Concession sequence
   - Trade-offs to offer
   - Red lines
   - Bundling strategy

4. CLOSING PHASE
   - Agreement documentation
   - Final terms review
   - Sign-off process
   - Communication plan

5. POST-NEGOTIATION
   - Relationship maintenance
   - Performance monitoring
   - Lessons learned

Output JSON:
{{
    "negotiation_plan": {{
        "phases": [
            {{
                "phase_name": "Preparation",
                "activities": [],
                "timeline": "1 week",
                "deliverables": [],
                "success_criteria": []
            }}
        ],
        "team_composition": [
            {{
                "role": "Lead Negotiator",
                "responsibilities": [],
                "required_skills": []
            }}
        ],
        "negotiation_roadmap": {{
            "total_duration": "3 weeks",
            "key_milestones": [],
            "decision_points": []
        }}
    }},
    "strategy_notes": {{
        "overall_approach": "Collaborative/Competitive/Integrative",
        "key_priorities": [],
        "non_negotiables": [],
        "trade_off_matrix": {{}}
    }},
    "risk_mitigation": [],
    "contingency_scenarios": []
}}

Negotiation Plan:"""

        response = await llm_client.generate(prompt, temperature=0.4)
        
        try:
            start_idx = response.find('{')
            end_idx = response.rfind('}') + 1
            
            if start_idx >= 0 and end_idx > start_idx:
                json_str = response[start_idx:end_idx]
                return json.loads(json_str)
        except json.JSONDecodeError:
            pass
        
        return {
            "negotiation_plan": {},
            "plan_text": response
        }
    
    async def _develop_concession_strategy(self, agent_input: AgentInput) -> Dict[str, Any]:
        """Develop strategic concession plan."""
        negotiation_items = agent_input.context.get("items", [])
        priorities = agent_input.context.get("priorities", {})
        
        prompt = f"""Develop strategic concession plan for negotiation.

Negotiation Items:
{json.dumps(negotiation_items, indent=2)}

Priorities:
{json.dumps(priorities, indent=2)}

Instructions: {agent_input.instructions}

Create concession strategy:

1. CONCESSION INVENTORY
   - All possible concessions
   - Value to us (cost)
   - Value to them (benefit)
   - Strategic importance

2. CONCESSION SEQUENCING
   - Initial concessions (low cost, high value to them)
   - Middle concessions (balanced)
   - Final concessions (high cost, high importance)
   - Never concessions (non-negotiable)

3. RECIPROCITY STRATEGY
   - What to ask in return
   - Equivalent value trades
   - Package deals
   - Conditional concessions

4. TIMING AND PACING
   - When to make concessions
   - Speed of concession
   - Escalation strategy
   - De-escalation tactics

Output JSON:
{{
    "concession_matrix": [
        {{
            "concession_item": "Item name",
            "category": "Price/Terms/Scope/Timeline",
            "cost_to_us": "High/Medium/Low",
            "value_to_them": "High/Medium/Low",
            "strategic_value": 0.8,
            "sequence_order": 1,
            "conditions": "Only if they...",
            "ask_in_return": "We should get...",
            "negotiable": true
        }}
    ],
    "concession_sequence": [
        {{
            "round": 1,
            "concessions_to_offer": [],
            "demands_to_make": [],
            "rationale": "Why this sequence"
        }}
    ],
    "reciprocity_rules": {{
        "never_concede_first": true,
        "always_ask_return": true,
        "matching_principle": "For every X, get Y"
    }},
    "escalation_path": [],
    "walk_away_triggers": []
}}

Concession Strategy:"""

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
            "concession_matrix": [],
            "strategy_text": response
        }
    
    async def _comprehensive_negotiation_strategy(self, agent_input: AgentInput) -> Dict[str, Any]:
        """Develop comprehensive negotiation strategy."""
        # Combine all analyses
        counter_offer_result = await self._generate_counter_offer(agent_input)
        leverage_result = await self._analyze_leverage(agent_input)
        plan_result = await self._create_negotiation_plan(agent_input)
        concession_result = await self._develop_concession_strategy(agent_input)
        
        return {
            "comprehensive_strategy": {
                "counter_offers": counter_offer_result,
                "leverage_analysis": leverage_result,
                "negotiation_plan": plan_result,
                "concession_strategy": concession_result
            },
            "executive_summary": self._create_executive_summary(
                counter_offer_result,
                leverage_result,
                plan_result
            ),
            "strategy_notes": self._generate_strategy_notes(
                counter_offer_result,
                leverage_result,
                concession_result
            ),
            "timestamp": datetime.utcnow().isoformat()
        }
    
    def _create_executive_summary(
        self,
        counter_offers: Dict,
        leverage: Dict,
        plan: Dict
    ) -> Dict[str, Any]:
        """Create executive summary of negotiation strategy."""
        return {
            "recommended_approach": "Collaborative with clear boundaries",
            "key_priorities": [
                "Secure favorable pricing terms",
                "Maintain long-term relationship",
                "Ensure quality standards"
            ],
            "success_probability": 0.75,
            "estimated_duration": "2-3 weeks",
            "critical_success_factors": [
                "Strong preparation",
                "Unified team approach",
                "Flexibility on non-essentials"
            ]
        }
    
    def _generate_strategy_notes(
        self,
        counter_offers: Dict,
        leverage: Dict,
        concessions: Dict
    ) -> List[str]:
        """Generate tactical strategy notes."""
        notes = [
            "Lead with relationship building before discussing terms",
            "Use data and benchmarks to support positions",
            "Prepare for multiple rounds of discussion",
            "Keep options open until final agreement",
            "Document all agreed points immediately",
            "Maintain professional tone throughout",
            "Focus on mutual value creation",
            "Be prepared to walk away if necessary"
        ]
        
        # Add leverage-specific notes
        power_balance = leverage.get("leverage_analysis", {}).get("power_balance", "Balanced")
        if power_balance == "Favorable":
            notes.append("Leverage our strong position but avoid overreach")
        elif power_balance == "Unfavorable":
            notes.append("Focus on creative solutions and long-term value")
        
        return notes
    
    def _calculate_confidence(self, result: Dict) -> float:
        """Calculate confidence in negotiation strategy."""
        confidence = 0.75
        
        if "comprehensive_strategy" in result:
            confidence += 0.15
        
        if result.get("counter_offers") or result.get("concession_matrix"):
            confidence += 0.05
        
        return min(confidence, 0.90)


# Global enhanced negotiation strategy agent instance
negotiation_strategy_agent_enhanced = NegotiationStrategyAgentEnhanced()
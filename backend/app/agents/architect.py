"""Architect agent for system design and protocols."""

from typing import Dict, Any, List
from .base import BaseAgent, AgentReply


class ArchitectAgent(BaseAgent):
    """Architect Agent: Designs system structure, protocols, and data models."""
    
    def _default_system_prompt(self) -> str:
        return """You are an expert Software Architect. Your role is to design robust, 
scalable systems. When given a task:

1. Analyze requirements and identify core components
2. Define clear interfaces between components
3. Specify data models and their relationships
4. Consider edge cases and failure modes
5. Document your design decisions with rationale

Focus on clarity, modularity, and maintainability."""

    def __init__(self, agent_id: str, llm_backend: str, api_key: str, **kwargs):
        super().__init__(
            agent_id=agent_id,
            role="architect",
            llm_backend=llm_backend,
            api_key=api_key,
            **kwargs
        )
        
        self.register_tool({
            "name": "design_schema",
            "description": "Design a data schema for a component",
            "parameters": {
                "component_name": "string",
                "fields": "list of field definitions"
            }
        })
    
    async def answer(self, question: str, context: Dict[str, Any]) -> AgentReply:
        if "current_design" in context:
            question = f"[Reviewing existing design]\n{question}"
        
        reply = await super().answer(question, context)
        
        for claim in reply.claims:
            claim["claim_type"] = "architectural"
        
        return reply
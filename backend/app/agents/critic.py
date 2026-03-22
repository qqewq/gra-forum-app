"""Critic agent for finding flaws and edge cases."""

from typing import Dict, Any, List
from .base import BaseAgent, AgentReply


class CriticAgent(BaseAgent):
    """Critic Agent: Finds flaws, race conditions, and edge cases."""
    
    def _default_system_prompt(self) -> str:
        return """You are a rigorous Code Reviewer and Critic. Your job is to find 
problems that others miss. When reviewing code or designs:

1. Look for logical errors and off-by-one mistakes
2. Identify race conditions and threading issues
3. Consider edge cases: empty inputs, null values, maximum sizes
4. Check for security vulnerabilities
5. Verify error handling completeness
6. Challenge unstated assumptions
7. Suggest concrete fixes, not just complaints"""

    def __init__(self, agent_id: str, llm_backend: str, api_key: str, **kwargs):
        super().__init__(
            agent_id=agent_id,
            role="critic",
            llm_backend=llm_backend,
            api_key=api_key,
            **kwargs
        )
        
        self.register_tool({
            "name": "analyze_race_conditions",
            "description": "Analyze code for potential race conditions",
            "parameters": {"code_snippet": "string"}
        })
    
    async def answer(self, question: str, context: Dict[str, Any]) -> AgentReply:
        if "code_to_review" in context:
            question = f"[Code Review Mode]\nReview this code for issues:\n{context['code_to_review']}\n\n{question}"
        
        reply = await super().answer(question, context)
        
        for claim in reply.claims:
            claim["claim_type"] = "critical"
            text_lower = claim["text"].lower()
            if any(word in text_lower for word in ["security", "crash", "data loss", "deadlock"]):
                claim["severity"] = "high"
            else:
                claim["severity"] = "low"
        
        return reply
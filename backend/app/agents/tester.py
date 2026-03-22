"""Tester agent for generating tests and chaos testing."""

from typing import Dict, Any, List, Optional
import random
from .base import BaseAgent, AgentReply


class TesterAgent(BaseAgent):
    """Tester Agent: Generates tests, fuzzing, and simple chaos testing."""
    
    def _default_system_prompt(self) -> str:
        return """You are an expert Software Tester. Your mission is to break things 
before users do. When testing:

1. Generate tests for happy paths, edge cases, and error conditions
2. Use property-based testing principles
3. Design chaos tests: random delays, failures, concurrent access
4. Include negative tests (what should NOT happen)
5. Write clear test names that describe the scenario"""

    def __init__(
        self, 
        agent_id: str, 
        llm_backend: str, 
        api_key: str,
        tests_runner: Optional[Any] = None,
        **kwargs
    ):
        super().__init__(
            agent_id=agent_id,
            role="tester",
            llm_backend=llm_backend,
            api_key=api_key,
            **kwargs
        )
        self.tests_runner = tests_runner
    
    async def answer(self, question: str, context: Dict[str, Any]) -> AgentReply:
        if "code_under_test" in context:
            question = f"[Testing Task]\nCode to test:\n{context['code_under_test']}\n\n{question}"
        
        reply = await super().answer(question, context)
        
        for claim in reply.claims:
            text_lower = claim["text"].lower()
            if any(word in text_lower for word in ["fuzz", "random", "chaos"]):
                claim["claim_type"] = "chaos_test"
            else:
                claim["claim_type"] = "test_case"
        
        return reply
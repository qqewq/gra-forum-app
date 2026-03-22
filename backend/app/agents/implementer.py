"""Implementer agent for writing code and running tests."""

from typing import Dict, Any, List, Optional
from .base import BaseAgent, AgentReply


class ImplementerAgent(BaseAgent):
    """Implementer Agent: Writes code and runs tests."""
    
    def _default_system_prompt(self) -> str:
        return """You are an expert Software Implementer. Your job is to write 
production-quality code. When implementing:

1. Follow the provided architecture and interfaces exactly
2. Write self-documenting code with clear variable names
3. Include docstrings and type hints
4. Handle errors gracefully with appropriate exceptions
5. Write efficient but readable code
6. Include inline comments for complex logic"""

    def __init__(
        self, 
        agent_id: str, 
        llm_backend: str, 
        api_key: str,
        code_runner: Optional[Any] = None,
        **kwargs
    ):
        super().__init__(
            agent_id=agent_id,
            role="implementer",
            llm_backend=llm_backend,
            api_key=api_key,
            **kwargs
        )
        self.code_runner = code_runner
        
        self.register_tool({
            "name": "implement_function",
            "description": "Implement a specific function with signature",
            "parameters": {
                "function_signature": "string",
                "requirements": "list",
                "language": "string"
            }
        })
    
    async def answer(self, question: str, context: Dict[str, Any]) -> AgentReply:
        if "specification" in context:
            question = f"[Implementation Task]\nSpecification:\n{context['specification']}\n\n{question}"
        
        reply = await super().answer(question, context)
        reply.metadata["code_blocks"] = self._extract_code_blocks(reply.text)
        
        return reply
    
    def _extract_code_blocks(self, text: str) -> List[Dict[str, Any]]:
        import re
        pattern = r'```(\w+)?\n(.*?)```'
        matches = re.findall(pattern, text, re.DOTALL)
        return [
            {"language": lang or "text", "code": code.strip()}
            for lang, code in matches
        ]
"""Base agent interface for gra-forum-app."""

from abc import ABC, abstractmethod
from typing import Dict, Any, List, Optional
from dataclasses import dataclass
import asyncio


@dataclass
class AgentReply:
    """Structured reply from an agent."""
    text: str
    claims: List[Dict[str, Any]]
    metadata: Dict[str, Any]
    tool_calls: Optional[List[Dict[str, Any]]] = None


class BaseAgent(ABC):
    """Abstract base class for all software engineering agents."""
    
    def __init__(
        self,
        agent_id: str,
        role: str,
        llm_backend: str,
        api_key: str,
        system_prompt: Optional[str] = None,
        temperature: float = 0.7
    ):
        self.agent_id = agent_id
        self.role = role
        self.llm_backend = llm_backend
        self.api_key = api_key
        self.system_prompt = system_prompt or self._default_system_prompt()
        self.temperature = temperature
        self.tools: List[Dict[str, Any]] = []
        
    @abstractmethod
    def _default_system_prompt(self) -> str:
        pass
    
    def register_tool(self, tool_def: Dict[str, Any]) -> None:
        self.tools.append(tool_def)
    
    async def answer(self, question: str, context: Dict[str, Any]) -> AgentReply:
        full_prompt = self._build_prompt(question, context)
        response = await self._call_llm(full_prompt)
        claims = self._extract_claims(response)
        
        return AgentReply(
            text=response,
            claims=claims,
            metadata={
                "agent_id": self.agent_id,
                "role": self.role,
                "llm_backend": self.llm_backend,
                "temperature": self.temperature
            }
        )
    
    def _build_prompt(self, question: str, context: Dict[str, Any]) -> str:
        prompt_parts = [f"System: {self.system_prompt}\n"]
        
        if "history" in context and context["history"]:
            prompt_parts.append("=== Previous Debate History ===")
            for round_data in context["history"]:
                prompt_parts.append(f"Round {round_data.get('round', '?')}:")
                for agent_reply in round_data.get("replies", []):
                    prompt_parts.append(f"  {agent_reply.get('agent_id')}: {agent_reply.get('text', '')[:200]}...")
            prompt_parts.append("")
        
        prompt_parts.append(f"=== Current Task ===\n{question}\n")
        return "\n".join(prompt_parts)
    
    async def _call_llm(self, prompt: str) -> str:
        await asyncio.sleep(0.1)
        return f"[{self.agent_id} response] Based on my role as {self.role}, I analyze: {prompt[:100]}..."
    
    def _extract_claims(self, text: str) -> List[Dict[str, Any]]:
        import re
        sentences = re.split(r'[.!?]+', text)
        claims = []
        for i, sent in enumerate(sentences[:5]):
            sent = sent.strip()
            if len(sent) > 10:
                claims.append({
                    "id": f"{self.agent_id}_claim_{i}",
                    "text": sent,
                    "agent_id": self.agent_id,
                    "confidence": 0.8
                })
        return claims
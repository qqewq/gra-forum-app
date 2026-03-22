"""Software Engineering Task Orchestrator using gra-forum."""

from typing import List, Dict, Any, Optional
import warnings

try:
    from gra_forum.core import GRACore, FoamWeights
    GRA_FORUM_AVAILABLE = True
except ImportError:
    GRA_FORUM_AVAILABLE = False
    warnings.warn("gra-forum library not available. Some features will be limited.")

from ..agents.base import BaseAgent


class SoftwareOrchestrator:
    """Orchestrator for software engineering tasks using GRA debate."""
    
    def __init__(
        self,
        agents: List[BaseAgent],
        core: Optional[Any] = None,
        max_rounds: int = 5,
        convergence_threshold: float = 0.1,
        tools: Optional[Dict[str, Any]] = None
    ):
        self.software_agents = {a.agent_id: a for a in agents}
        self.tools = tools or {}
        self.debate_history: List[Dict[str, Any]] = []
        self.foam_trajectory: List[float] = []
        self.max_rounds = max_rounds
        
        if core is not None:
            self.core = core
        elif GRA_FORUM_AVAILABLE:
            self.core = GRACore(weights=FoamWeights(
                conflict=0.4, vacuity=0.35, redundancy=0.2, noise=0.05
            ))
        else:
            self.core = None
    
    async def run_structured_debate(
        self, 
        task_spec: str,
        task_type: str = "full_implementation",
        context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        context = context or {}
        
        if task_type in ["design", "full_implementation"]:
            arch_result = await self._run_architecture_phase(task_spec, context)
            context["architecture"] = arch_result
        else:
            arch_result = context.get("architecture", {})
        
        if task_type in ["implementation", "full_implementation"]:
            impl_result = await self._run_implementation_phase(task_spec, context)
            context["implementation"] = impl_result
        else:
            impl_result = context.get("implementation", {})
        
        review_result = await self._run_review_phase(task_spec, context)
        
        return {
            "task_spec": task_spec,
            "task_type": task_type,
            "phases": {
                "architecture": arch_result,
                "implementation": impl_result,
                "review": review_result
            },
            "debate_history": self.debate_history,
            "foam_trajectory": self.foam_trajectory,
            "deliverables": self._compile_deliverables(context)
        }
    
    async def _run_architecture_phase(
        self, task_spec: str, context: Dict[str, Any]
    ) -> Dict[str, Any]:
        arch_agent = self._get_agent_by_role("architect")
        critic_agent = self._get_agent_by_role("critic")
        
        arch_reply = await arch_agent.answer(f"Design the architecture for: {task_spec}", context)
        critic_reply = await critic_agent.answer(
            "Review this architecture", {**context, "design_to_review": arch_reply.text}
        )
        
        round_data = {
            "phase": "architecture",
            "round": 1,
            "replies": [
                {"agent_id": arch_agent.agent_id, "text": arch_reply.text, "claims": arch_reply.claims},
                {"agent_id": critic_agent.agent_id, "text": critic_reply.text, "claims": critic_reply.claims}
            ]
        }
        self.debate_history.append(round_data)
        
        foam = self._calculate_foam_for_round(round_data)
        self.foam_trajectory.append(foam)
        
        return {
            "design": arch_reply.text,
            "criticism": critic_reply.text,
            "foam": foam
        }
    
    async def _run_implementation_phase(
        self, task_spec: str, context: Dict[str, Any]
    ) -> Dict[str, Any]:
        impl_agent = self._get_agent_by_role("implementer")
        tester_agent = self._get_agent_by_role("tester")
        
        impl_reply = await impl_agent.answer(
            f"Implement: {task_spec}\nArchitecture: {context.get('architecture', {}).get('design', 'N/A')}",
            context
        )
        test_reply = await tester_agent.answer(
            "Generate comprehensive tests",
            {**context, "code_under_test": impl_reply.text}
        )
        
        round_data = {
            "phase": "implementation",
            "round": len(self.debate_history) + 1,
            "replies": [
                {"agent_id": impl_agent.agent_id, "text": impl_reply.text, "claims": impl_reply.claims},
                {"agent_id": tester_agent.agent_id, "text": test_reply.text, "claims": test_reply.claims}
            ]
        }
        self.debate_history.append(round_data)
        
        foam = self._calculate_foam_for_round(round_data)
        self.foam_trajectory.append(foam)
        
        return {
            "code": impl_reply.text,
            "tests": test_reply.text,
            "foam": foam
        }
    
    async def _run_review_phase(
        self, task_spec: str, context: Dict[str, Any]
    ) -> Dict[str, Any]:
        critic_agent = self._get_agent_by_role("critic")
        
        review_prompt = (
            f"Final review for: {task_spec}\n\n"
            f"Code:\n{context.get('implementation', {}).get('code', 'N/A')}\n\n"
            "Provide final review and approval status."
        )
        
        reply = await critic_agent.answer(review_prompt, context)
        
        return {
            "final_review": reply.text,
            "consensus_reached": "approved" in reply.text.lower() or "looks good" in reply.text.lower()
        }
    
    def _get_agent_by_role(self, role: str) -> BaseAgent:
        for agent in self.software_agents.values():
            if agent.role == role:
                return agent
        raise ValueError(f"No agent found with role: {role}")
    
    def _calculate_foam_for_round(self, round_data: Dict[str, Any]) -> float:
        all_claims = []
        for reply in round_data.get("replies", []):
            all_claims.extend(reply.get("claims", []))
        
        if self.core is not None and hasattr(self.core, 'compute_foam'):
            try:
                return self.core.compute_foam(all_claims)
            except:
                pass
        
        return min(1.0, len(all_claims) * 0.1)
    
    def _compile_deliverables(self, context: Dict[str, Any]) -> Dict[str, Any]:
        return {
            "architecture_spec": context.get("architecture", {}).get("design"),
            "implementation_code": context.get("implementation", {}).get("code"),
            "test_suite": context.get("implementation", {}).get("tests"),
            "known_issues": self._extract_issues_from_history()
        }
    
    def _extract_issues_from_history(self) -> List[str]:
        issues = []
        for round_data in self.debate_history:
            for reply in round_data.get("replies", []):
                if reply.get("agent_id") == "critic":
                    text = reply.get("text", "")
                    for line in text.split("\n"):
                        if any(marker in line.lower() for marker in ["issue", "problem", "bug", "flaw", "concern"]):
                            issues.append(line.strip())
        return issues
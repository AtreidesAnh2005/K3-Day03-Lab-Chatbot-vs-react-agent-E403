"""Safety critic agent."""

from multi_agent.state import AgentState
from services.privacy_guard import redact_sensitive_data


def run_safety_critic_agent(state: AgentState) -> AgentState:
    """Apply safety and privacy checks before final response."""
    if state.final_answer:
        state.final_answer = redact_sensitive_data(state.final_answer)
    state.trace.append("Safety critic agent completed")
    return state

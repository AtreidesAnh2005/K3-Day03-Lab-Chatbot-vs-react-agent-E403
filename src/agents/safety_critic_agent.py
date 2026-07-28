"""Safety critic that runs before every specialist."""

from multi_agent.state import AgentState
from services.privacy_guard import assess_request


def run_safety_critic_agent(state: AgentState) -> AgentState:
    state.record("safety_critic", "started")
    assessment = assess_request(state.user_query)
    state.safety_verdict = assessment["verdict"]
    state.record("safety_critic", "verdict", assessment)
    state.complete("safety_critic")
    return state

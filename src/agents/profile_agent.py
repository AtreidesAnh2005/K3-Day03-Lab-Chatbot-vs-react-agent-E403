"""Profile extraction agent."""

from multi_agent.state import AgentState
from tools.profile_tools import extract_profile


def run_profile_agent(state: AgentState) -> AgentState:
    """Extract user profile signals from the query."""
    state.profile = extract_profile(state.user_query)
    state.trace.append("Profile agent completed")
    return state

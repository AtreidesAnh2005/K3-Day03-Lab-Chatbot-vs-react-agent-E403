"""Candidate matching agent."""

from multi_agent.state import AgentState
from tools.matching_tools import find_candidate_matches


def run_matching_agent(state: AgentState) -> AgentState:
    """Find compatible candidates based on the current profile."""
    state.candidates = find_candidate_matches(state.profile)
    state.trace.append("Matching agent completed")
    return state
